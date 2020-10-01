import argparse
import datetime
import itertools
import json
import logging
import pathlib

from typing import Type, List

import pandas

import assets
import http_session
import maps
import objects
import settings
import ufdex
import utils
import exceptions

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
API documentation: https://ufapidocs.clients.builtonawesomeness.co.uk/
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true', help='Show more logging information')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--error', type=pathlib.Path, help='Error log file')
    parser.add_argument('-t', '--token', type=pathlib.Path, help='Path of file containing access token',
                        default=settings.DEFAULT_TOKEN_PATH)
    parser.add_argument('-r', '--reading_type_groups', type=pathlib.Path,
                        help="Configuration to group reading types into reading categories",
                        default=settings.DEFAULT_READING_TYPE_GROUPS_FILE)
    parser.add_argument('-a', '--aqi', help="Air quality standards JSON file",
                        default=settings.DEFAULT_AQI_STANDARDS_FILE, type=pathlib.Path)
    return parser.parse_args()


def sync_readings(session, sensors: list, awesome_sensors: dict, reading_types: dict):
    """
    Bulk store readings
    """

    def map_row_to_readings(_rows, sensor_name: str) -> iter:
        for row in _rows:
            # Convert rows of portal data into portal readings
            yield from maps.row_to_readings(row, sensor_name=sensor_name, reading_types=reading_types,
                                            awesome_sensors=awesome_sensors)

    for sensor in sensors:
        if ('[SCC]' in sensor['name']) or sensor['name'] == '21924':
            LOGGER.warning("Skipping sensor %s", sensor['name'])
            continue
        LOGGER.info("Sensor %s", sensor['name'])

        # Get the beginning of the time period
        _sensor = assets.Sensor(sensor['name'])
        start_time = _sensor.latest_timestamp

        # Default earliest time
        if not start_time:
            start_time = settings.TIME_START

        # Update from the latest record in the database -- either keep a bookmark or run a MAX query
        query = dict(
            sensors={sensor['name']},
            time_period=[
                start_time,
                datetime.datetime.now(datetime.timezone.utc),
            ],

        )
        query = ufdex.UrbanFlowsQuery(**query)
        rows = query()

        # Iterate over data chunks
        for chunk in utils.iter_chunks(map_row_to_readings(rows, sensor_name=sensor['name']),
                                       chunk_size=settings.BULK_READINGS_CHUNK_SIZE):
            if chunk:
                try:
                    objects.Reading.store_bulk(session, readings=chunk)
                # No more readings, so stop
                except exceptions.EmptyValueError:
                    break

            # Record progress through the stream
            latest_timestamp = max([row['timestamp'] for row in chunk])
            _sensor.latest_timestamp = latest_timestamp


def sync_sites(session: http_session.PortalSession, sites: iter, locations: dict):
    """
    Convert UFO sites into Awesome locations.

    Either update or create a new location for each site.

    :param session: Awesome portal HTTP session
    :param sites: UFO sites
    :param locations: Map of Awesome location names to identifiers
    """

    for site in sites:
        LOGGER.debug("SITE %s", site)

        # Convert to Awesome object
        location = maps.site_to_location(site)

        try:
            # Retrieve existing location
            location_id = locations[site['name']]
            loc = objects.Location(location_id)

            # Amend existing location
            loc.update(session, location)

        # Location doesn't exist on in Awesome database
        except KeyError:

            # Create new location
            body = objects.Location.add(session, location)
            new_location = body['data']

            # Store id of new location
            locations[new_location['name']] = new_location['id']


def sync_sensors(session: http_session.PortalSession, sensors, awesome_sensors, locations: dict):
    """
    Either update or create a new location for each site

    :param session: Awesome portal HTTP session
    :param sensors: UFO sensors
    :param awesome_sensors: Awesome portal sensors
    :param locations: Map of Awesome location name to identifier
    """

    for sensor in sensors:

        # Convert to Awesome object
        awe_sensor = maps.sensor_to_sensor(sensor, locations)

        try:
            sensor_id = awesome_sensors[sensor['name']]
            sen = objects.Sensor(sensor_id)
            sen.update(session, awe_sensor)

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new
            body = objects.Sensor.add(session, awe_sensor)
            new_sensor = body['data']

            # Store id of new sensor
            awesome_sensors[new_sensor['name']] = new_sensor['id']


def sync_reading_types(session: http_session.PortalSession, detectors: dict, reading_types: dict):
    # Iterate over detectors
    for detector_name, detector in detectors.items():

        LOGGER.info("DETECTOR %s %s", detector_name, detector)

        obj = maps.detector_to_reading_type(detector)

        try:
            reading_type_id = reading_types[detector['name']]

            # Add/update a reading type
            reading_type = objects.ReadingType(reading_type_id)
            reading_type.update(session, obj)

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new
            body = objects.ReadingType.add(session, obj)
            new_reading_type = body['data']
            reading_types[new_reading_type['name']] = new_reading_type['id']


def load_reading_category_config(path: pathlib.Path) -> list:
    with pathlib.Path(path).open() as file:
        return json.load(file)


def sync_reading_categories(session, reading_categories: dict, reading_type_groups: list):
    LOGGER.debug("READING CATEGORIES: %s", reading_categories)

    for read_cat in reading_type_groups:
        obj = objects.ReadingCategory.new(name=read_cat['name'], icon_name=read_cat['icon_name'])

        try:
            # Update existing reading category
            reading_category_id = reading_categories[read_cat['name']]
            reading_category = objects.ReadingCategory(reading_category_id)
            reading_category.update(session, obj=obj)

        except KeyError:
            # Make new reading category
            body = objects.ReadingCategory.add(session, obj)
            new_reading_category = body['data']
            reading_categories[new_reading_category['name']] = new_reading_category['id']


def get_urban_flows_metadata() -> tuple:
    """Retrieve all Urban Flows metadata"""

    sites, families, pairs, sensors = assets.get_metadata()

    # Get a mapping of all detectors on all sensors
    # Each sensor pod contains multiple detectors (quantitative measurement channels)
    # Different sensors may have detectors (channels) with the same name (but different properties perhaps)
    detectors = {det['name']: det for det in itertools.chain(*(s['detectors'].values() for s in sensors))}

    return sites, families, pairs, sensors, detectors


def build_awesome_object_map(session: http_session.PortalSession, cls: Type[objects.AwesomeObject]) -> dict:
    """
    Map Awesome object names to identifiers
    """
    return {obj['name']: obj['id'] for obj in cls.list_iter(session)}


def load_aqi_standards(path: pathlib.Path) -> List[dict]:
    with path.open() as file:
        return json.load(file)


def sync_aqi_standards(session, aqi_standards_file):
    standards = load_aqi_standards(aqi_standards_file)

    for standard in standards:
        data = objects.AQIStandard.new(name=standard['name'], description=standard.get('description'),
                                       breakpoints=standard['breakpoints'])

        objects.AQIStandard.add(session, data)


def sync_aqi_readings(session, sites, locations: dict):
    import aqi.operations

    for site in sites:
        # Get the latest timestamp that was successfully synced (or the default start date)
        site_obj = assets.Site(site['name'])
        bookmark = site_obj.latest_timestamp or settings.TIME_START

        LOGGER.info("Site %s, latest timestamp %s", site['name'], bookmark)

        data = aqi.operations.get_urban_flows_data(site_id=site['name'], start=bookmark)

        # Skip missing data
        if data.empty:
            continue

        air_quality_index = aqi.operations.calculate_air_quality(data)['air_quality_index'].dropna()

        if air_quality_index.empty:
            continue

        location_id = locations[site['name']]

        readings = maps.aqi_readings(air_quality_index, aqi_standard_id=1, location_id=location_id)

        # Sync readings (The aqi readings input must have between 1 and 100 items.)
        for chunk in utils.iter_chunks(readings, chunk_size=settings.BULK_READINGS_CHUNK_SIZE):
            objects.AQIReading.store_bulk(session, aqi_readings=chunk)

        # Update bookmark on success
        new_timestamp = data.index.max()
        if not pandas.isnull(new_timestamp):
            site_obj.latest_timestamp = new_timestamp.to_pydatetime()


def sync(session, reading_type_groups: list, aqi_standards_file: pathlib.Path):
    """Update or add metadata objects to the Awesome web portal"""

    # Get UFO metadata
    sites, families, pairs, sensors, detectors = get_urban_flows_metadata()

    LOGGER.info('Retrieving portal objects...')

    # Map location name to location identifier
    awesome_sensors = build_awesome_object_map(session, objects.Sensor)
    locations = build_awesome_object_map(session, objects.Location)
    reading_types = build_awesome_object_map(session, objects.ReadingType)
    reading_categories = build_awesome_object_map(session, objects.ReadingCategory)

    # TODO skip unchanged objects (don't update if no changes). Perhaps list all Awesome objects and compare to find
    # differences.

    sync_aqi_standards(session, aqi_standards_file=aqi_standards_file)
    sync_aqi_readings(session, sites=sites, locations=locations)
    #
    # LOGGER.info('Syncing Urban Flows Sites to Awesome Locations...')
    # sync_sites(session, sites, locations=locations)
    #
    # LOGGER.info('Syncing sensors...')
    # sync_sensors(session, sensors, awesome_sensors=awesome_sensors, locations=locations)
    #
    # LOGGER.info('Syncing reading types...')
    # sync_reading_types(session, detectors=detectors, reading_types=reading_types)
    #
    # LOGGER.info('Syncing reading categories...')
    # sync_reading_categories(session, reading_categories=reading_categories, reading_type_groups=reading_type_groups)

    # Sync data
    # sync_readings(session=session, reading_types=reading_types, sensors=sensors, awesome_sensors=awesome_sensors)


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    reading_type_groups = load_reading_category_config(args.reading_type_groups)

    # Connect to Awesome portal
    with http_session.PortalSession(token_path=args.token) as session:
        sync(session, reading_type_groups=reading_type_groups, aqi_standards_file=args.aqi)


if __name__ == '__main__':
    main()

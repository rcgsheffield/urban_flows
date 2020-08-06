import argparse
import itertools
import json
import logging
import datetime
import pathlib

import ufportal.assets
import ufportal.settings
import ufportal.awesome_utils
import ufportal.http_session
import ufportal.maps
import ufportal.objects
import ufportal.ufdex
import ufportal.utils

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
API documentation: https://ufapidocs.clients.builtonawesomeness.co.uk/
"""

# TODO
USAGE = """
python -m ufportal
"""


def get_args():
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true', help='Show more logging information')
    parser.add_argument('-t', '--token', type=pathlib.Path, help='Path of file containing access token',
                        default=ufportal.settings.DEFAULT_TOKEN_PATH)
    return parser.parse_args()


def add_readings(session, rows: iter, sensors: dict, reading_types: dict):
    def get_readings(_rows) -> iter:
        for row in _rows:
            yield from ufportal.maps.row_to_readings(row, sensors=sensors, reading_types=reading_types)

    for chunk in ufportal.utils.iter_chunks(get_readings(rows), size=100):
        ufportal.objects.Reading.store_bulk(session, readings=chunk)


def sync_sites(session, sites, locations):
    """Either update or create a new location for each site"""

    for site in sites:
        LOGGER.debug("SITE %s", site)

        # Convert to Awesome object
        location = ufportal.maps.site_to_location(site)

        try:
            # Retrieve existing location
            location_id = locations[site['name']]
            loc = ufportal.objects.Location(location_id)

            # Amend existing location
            data = loc.update(session, location)

        # Location doesn't exist on in Awesome database
        except KeyError:

            # Create new location
            data = ufportal.objects.Location.add(session, location)

        LOGGER.debug("LOCATION RESPONSE %s", data)


def sync_sensors(session, sensors, awesome_sensors, locations):
    """Either update or create a new location for each site"""

    for sensor in sensors:

        # Convert to Awesome object
        awe_sensor = ufportal.maps.sensor_to_sensor(sensor, locations)

        try:
            sensor_id = awesome_sensors[sensor['name']]
            sen = ufportal.objects.Sensor(sensor_id)
            sen.update(session, awe_sensor)

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new
            ufportal.objects.Sensor.add(session, awe_sensor)


def sync_reading_types(session, detectors, reading_types):
    # Iterate over detectors
    for detector in detectors:

        obj = ufportal.maps.detector_to_reading_type(detector)

        try:
            reading_type_id = reading_types[detector['name']]

            # Add/update a reading type
            reading_type = ufportal.objects.ReadingType(reading_type_id)
            reading_type.update(session, obj)

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new
            ufportal.objects.ReadingType.add(session, obj)


def load_reading_category_config() -> list:
    with open('reading_categories.json') as file:
        return json.load(file)


def sync_reading_categories(session, reading_categories):
    config = load_reading_category_config()

    for read_cat in config:
        obj = ufportal.objects.ReadingCategory.new(name=read_cat['name'], icon_name=read_cat['icon_name'])

        # Update existing reading category
        reading_category_id = reading_categories[read_cat['name']]
        reading_category = ufportal.objects.ReadingCategory(reading_category_id)
        reading_category.update(session, obj=obj)


def get_urban_flows_metadata() -> tuple:
    """Retrieve all Urban Flows metadata"""

    sites, families, pairs, sensors = ufportal.assets.get_metadata()

    # Get a mapping of all detectors on all sensors
    # Each sensor pod contains multiple detectors (quantitative measurement channels)
    detectors = {det['name'].upper(): det for det in itertools.chain(*(s['detectors'].values() for s in sensors))}

    return sites, families, pairs, sensors, detectors


def sync(session):
    """Update or add metadata objects to the Awesome web portal"""

    # Get UFO metadata
    sites, families, pairs, sensors, detectors = get_urban_flows_metadata()

    LOGGER.info('Retrieving portal objects...')

    # Map location name to location identifier
    awesome_sensors = {obj['name']: obj['id'] for obj in ufportal.objects.Sensor.list_iter(session)}
    locations = {obj['name']: obj['id'] for obj in ufportal.objects.Location.list_iter(session)}
    reading_types = {obj['name']: obj['id'] for obj in ufportal.objects.ReadingType.list_iter(session)}
    reading_categories = {obj['name']: obj['id'] for obj in ufportal.objects.ReadingCategory.list_iter(session)}

    # Update Awesome portal to match UFO
    LOGGER.info('Syncing Urban Flows Sites to Awesome Locations...')
    sync_sites(session, sites, locations=locations)

    LOGGER.info('Syncing sensors...')
    sync_sensors(session, sensors, awesome_sensors=awesome_sensors, locations=locations)

    LOGGER.info('Syncing reading types...')
    sync_reading_types(session, detectors=detectors, reading_types=reading_types)

    LOGGER.info('Syncing reading categories...')
    sync_reading_categories(session, reading_categories=reading_categories)

    # Sync data
    # Update from the latest record in the database -- either keep a bookmark or run a MAX query
    # TODO
    query = dict(
        time_period=[
            datetime.datetime(2020, 3, 2),
            datetime.datetime(2020, 3, 3),
        ],
    )
    add_readings(session=session, rows=ufportal.ufdex.run(query), reading_types=reading_types, sensors=sensors)


def main():
    args = get_args()
    ufportal.utils.configure_logging(verbose=args.verbose)

    # Connect to Awesome portal
    with ufportal.http_session.PortalSession(token_path=args.token) as session:
        sync(session)


if __name__ == '__main__':
    main()

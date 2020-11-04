import datetime
import json
import logging
import pathlib
import http
from typing import Type, List, Union

import requests
import pandas
import arrow

import assets
import exceptions
import http_session
import maps
import objects
import settings
import ufdex
import utils

LOGGER = logging.getLogger(__name__)

Path = Union[pathlib.Path, str]


def sync_readings(session, sensors: list, awesome_sensors: dict, reading_types: dict):
    """
    Bulk store readings
    """

    def rename(row: dict, key_map: dict) -> dict:
        for old_key, new_key in key_map.items():
            row[new_key] = row.pop(old_key)
        return row

    def map_row_to_readings(_rows, sensor_name: str) -> iter:
        for row in _rows:
            # Convert rows of portal data into portal readings
            yield from maps.row_to_readings(row, sensor_name=sensor_name, reading_types=reading_types,
                                            awesome_sensors=awesome_sensors)

    for sensor in sensors:

        # Skip these, they seem to cause problems
        if ('[SCC]' in sensor['name']) or sensor['name'] == '21924':
            # TODO don't skip SCC sensors
            LOGGER.warning("Skipping sensor %s", sensor['name'])
            continue

        LOGGER.info("Sensor %s", sensor['name'])

        # Get the beginning of the time period
        sensor_asset = assets.Sensor(sensor['name'])
        start_time = sensor_asset.latest_timestamp

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
        rows = (rename(row, key_map=settings.UF_COLUMN_RENAME) for row in rows)

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
            # Get the greatest timestamp in that chunk (assuming all input data is chronological)
            latest_timestamp = max([row['created'] for row in chunk])  # the 'created' timestamp is a string
            sensor_asset.latest_timestamp = utils.parse_timestamp(latest_timestamp)


def sync_sites(session: http_session.PortalSession, sites: iter, locations: dict):
    """
    Convert UFO sites into Awesome locations.

    Create a new location for each site if it doesn't already exist. Locations cannot be updated.
    then do nothing.

    :param session: Awesome portal HTTP session
    :param sites: UFO sites
    :param locations: Map of remote Awesome location names to object data
    """

    for site in sites:
        LOGGER.debug("SITE %s", site)

        # Convert UFO site to Awesome object
        local_location = maps.site_to_location(site)

        # Does this location exist on the Awesome portal?
        if site['name'] not in locations.keys():
            # Create new location
            body = objects.Location.add(session, local_location)
            new_location = body['data']

            # Store id of new location
            locations[new_location['name']] = new_location['id']


def sync_sensors(session: http_session.PortalSession, sensors, awesome_sensors: dict, locations: dict):
    """
    Either update (if changed) or create a new Awesome sensor for each Urban Flows sensor. For each sensor, if no
    changes have been made to the UFO sensor metadata then do nothing.

    :param session: Awesome portal HTTP session
    :param sensors: UFO sensors
    :param awesome_sensors: Awesome portal sensors
    :param locations: Map of Awesome location name to object
    """

    # Iterate over UFO sensors
    for sensor in sensors:

        # Convert to Awesome object
        local_sensor = maps.sensor_to_sensor(sensor, locations)

        try:
            remote_sensor = awesome_sensors[sensor['name']]

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new sensor
            body = objects.Sensor.add(session, local_sensor)
            new_sensor = body['data']

            # Store id of new sensor
            awesome_sensors[new_sensor['name']] = new_sensor['id']

            continue

        # Have changes been made?
        # Adjust the data structure to match the local object
        remote_sensor['location_id'] = remote_sensor['location']['id']
        if maps.is_object_different(local_sensor, remote_sensor):
            # Update the object on the Awesome portal
            sen = objects.Sensor(remote_sensor['id'])
            sen.update(session, local_sensor)


def sync_reading_types(session: http_session.PortalSession, detectors: dict, reading_types: dict,
                       remote_reading_category_ids: dict, reading_type_groups: list):
    """
    Map local Urban Flows Observatory "detectors" to remote "reading types" on the Awesome Portal.

    :param session: Awesome portal HTTP connection
    :param detectors: UFO metrics
    :param reading_types: Awesome metrics
    :param remote_reading_category_ids: Map of reading types to reading categories
    :param reading_type_groups: The local configuration for groups of reading types
    """
    # Map reading types to reading categories from local configuration file
    # This is the desired end-state configuration to sync to the remote server
    reading_type_name_to_category_ids = maps.reading_type_to_reading_categories(
        reading_type_groups=reading_type_groups,
        awesome_reading_categories=remote_reading_category_ids)

    # Iterate over UF detectors
    for detector_name, detector in detectors.items():

        LOGGER.info("DETECTOR %s %s", detector_name, detector)

        local_reading_type = maps.detector_to_reading_type(detector)

        try:
            # Does a reading type with this name exist in the database?
            remote_reading_type = reading_types[detector_name]

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new
            body = objects.ReadingType.add(session, local_reading_type)
            new_reading_type = body['data']
            reading_types[new_reading_type['name']] = new_reading_type
            continue

        # Add/update a reading type
        reading_type = objects.ReadingType(remote_reading_type['id'])
        reading_type.update(session, local_reading_type)

        # Reading categories
        try:
            remote_reading_category_ids = {rc['id'] for rc in reading_type.get(session)['reading_categories']}
        except KeyError:
            LOGGER.error(reading_type.get(session))
            raise

        try:
            local_reading_category_ids = reading_type_name_to_category_ids[detector_name]

        # No reading categories are configured for this reading type
        except KeyError:
            continue

        # Add new reading categories to this reading type
        for reading_category_id in set(local_reading_category_ids) - set(remote_reading_category_ids):
            reading_type.add_reading_category(session, reading_category_id)

        # Remove deleted items
        for reading_category_id in set(remote_reading_category_ids) - set(local_reading_category_ids):
            reading_type.remove_reading_category(session, reading_category_id)


def sync_reading_categories(session, reading_categories: dict, reading_type_groups: list):
    """
    Sync reading categories (e.g. "Air Quality" is a category containing reading types PM 1, PM 2.5, PM 10.)

    :param session: Awesome portal HTTP session
    :param reading_categories: Map existing Awesome reading category names to their object data
    :param reading_type_groups: Locally configured groups to be synced
    """
    LOGGER.debug("READING CATEGORIES: %s", reading_categories)

    for read_cat in reading_type_groups:
        # Case insensitive
        read_cat['name'] = read_cat['name'].upper()

        local_reading_category = objects.ReadingCategory.new(name=read_cat['name'], icon_name=read_cat['icon_name'])

        try:
            # Update existing reading category
            reading_category = reading_categories[read_cat['name']]
            reading_category = objects.ReadingCategory(reading_category['id'])
            reading_category.update(session, obj=local_reading_category)

        except KeyError:
            # Make new reading category
            body = objects.ReadingCategory.add(session, local_reading_category)
            new_reading_category = body['data']
            reading_categories[new_reading_category['name']] = new_reading_category['id']


def get_urban_flows_metadata() -> tuple:
    """Retrieve all Urban Flows metadata"""

    sites, families, pairs, sensors = assets.get_metadata()

    detectors = assets.get_detectors_from_sensors(sensors)

    return sites, families, pairs, sensors, detectors


def build_awesome_object_map(session: http_session.PortalSession, cls: Type[objects.AwesomeObject]) -> dict:
    """
    Map Awesome object names (case insensitive) to the object data
    """
    # Case-insensitive
    return {obj['name'].upper(): obj for obj in cls.list_iter(session)}


def load_json_objects(path: Path) -> List[dict]:
    """
    Load the AQI standards that you want to sync to the remote server.
    """
    with pathlib.Path(path).open() as file:
        return [dict(obj) for obj in json.load(file)]


def sync_aqi_standards(session, aqi_standards_file: Path):
    """
    Assume there's only one AQI standard and sync it.
    """

    local_standards = load_json_objects(aqi_standards_file)

    # Get first local AQI standard definition
    local_standard = local_standards[0]

    try:
        # Update the existing object
        obj = objects.AQIStandard(settings.AWESOME_AQI_STANDARD_ID)
        obj.update(session, local_standard)
    except requests.exceptions.HTTPError as e:
        # If it doesn't already exist then create it
        if e.response.status_code == http.HTTPStatus.NOT_FOUND:
            obj_data = objects.AQIStandard.new(**local_standard)
            objects.AQIStandard.add(session, obj_data)
        else:
            raise


def sync_aqi_readings(session, sites, locations: dict):
    import aqi.operations

    for site in sites:
        # Get the latest timestamp that was successfully synced (or the default start date)
        site_obj = assets.Site(site['name'])
        bookmark = site_obj.latest_timestamp or settings.TIME_START

        LOGGER.info("Site %s AQI readings. Latest timestamp %s", site['name'], bookmark)

        data = aqi.operations.get_urban_flows_data(site_id=site['name'], start=bookmark)

        # Skip missing data
        if data.empty:
            continue

        air_quality_index = aqi.operations.calculate_air_quality(data)['air_quality_index'].dropna()

        if air_quality_index.empty:
            continue

        location = locations[site['name']]

        readings = maps.aqi_readings(air_quality_index, aqi_standard_id=settings.AWESOME_AQI_STANDARD_ID,
                                     location_id=location['id'])

        # Sync readings (The aqi readings input must have between 1 and 100 items.)
        for chunk in utils.iter_chunks(readings, chunk_size=settings.BULK_READINGS_CHUNK_SIZE):
            objects.AQIReading.store_bulk(session, aqi_readings=chunk)

        # Update bookmark on success
        new_timestamp = data.index.max()
        if not pandas.isnull(new_timestamp):
            site_obj.latest_timestamp = new_timestamp.to_pydatetime()

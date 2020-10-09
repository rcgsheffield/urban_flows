"""
Map Urban Flows assets to Awesome portal objects.
"""

import logging

import pandas

import objects

LOGGER = logging.getLogger(__name__)


def awesome_coordinate(value: float) -> str:
    """Format a float as a ten-decimal-places string"""
    return "{:.10f}".format(value)


def site_to_location(site: dict) -> dict:
    """Map Urban Flows site to an Awesome portal location"""

    # Get latest activity
    activity = sorted(site['activity'], key=lambda act: act['t0'])[0]

    return objects.Location.new(
        name=str(site['name']),
        lat=awesome_coordinate(site['latitude']),
        lon=awesome_coordinate(site['longitude']),
        elevation=int(activity['heightAboveSL']),
    )


def sensor_latest_deployment(sensor: dict) -> dict:
    """
    Get latest site deployment
    """

    # Sort by deployment date (ascending)
    pairs = sorted(sensor['attachedTo'], key=lambda p: p['from'])

    pair = pairs[0]

    return pair


def sensor_to_sensor(sensor: dict, locations: dict) -> dict:
    """
    Map an Urban Flows sensor to an Awesome sensor
    """

    pair = sensor_latest_deployment(sensor)
    site_name = pair['site']

    return objects.Sensor.new(
        name=str(sensor['name']),
        location_id=locations[site_name]['id'],
        sensor_type_id=1,
        active=bool(sensor['isActive'])
    )


def detector_to_reading_type(detector: dict) -> dict:
    return objects.ReadingType.new(
        # Case insensitive
        name=detector['name'].upper(),
        unit=detector['u'].casefold() or 'unit',

        # Absolute maximum values the reading can take.
        # For example, temperature can never go below absolute zero of -273 C
        # TODO configure this on a per-reading-type basis
        min_value=0,
        max_value=999,
    )


def row_to_readings(row: dict, sensor_name: str, awesome_sensors: dict, reading_types) -> iter:
    """
    Convert a row of UFO data into multiple Awesome portal readings.

    :param row: UFO data row
    :param sensor_name: UFO sensor name
    :param reading_types: Awesome reading types
    :param awesome_sensors: Map Awesome sensor name to identifier
    :return: Generate readings
    """

    # Extract metadata (dimensions) common to all data columns
    time = row.pop('time')
    del row['sensor']
    awesome_sensor_id = awesome_sensors[sensor_name]

    del row['site_id']

    # Each row contains several readings (columns)
    for column_label, value in row.items():
        yield objects.Reading.new(
            sensor_id=awesome_sensor_id,
            reading_type_id=reading_types[column_label],
            value=value,
            created=time.isoformat(),
        )


def aqi_readings(air_quality_index: pandas.Series, aqi_standard_id: int, location_id: int) -> list:
    """

    """
    return [
        dict(
            created=timestamp.isoformat(),
            value=int(value),
            aqi_standard_id=aqi_standard_id,
            location_id=location_id,
        )
        for timestamp, value in air_quality_index.items()
    ]


def reading_type_to_reading_categories(reading_type_groups: list, awesome_reading_categories: dict) -> dict:
    """
    Map reading type names to Awesome reading category identifier

    :param reading_type_groups: The locally configured reading type groups (categories)
    :param awesome_reading_categories: The map of Awesome reading category names to their identifiers
    :return: A map of reading type names to Awesome reading category identifiers
    """
    # Build the mapping
    reading_type_name_to_reading_category_ids = dict()

    # Iterate over locally-defined reading type groups
    for reading_category in reading_type_groups:
        for reading_type in reading_category['reading_types']:

            # Initialise set
            if reading_type not in reading_type_name_to_reading_category_ids.keys():
                reading_type_name_to_reading_category_ids[reading_type] = set()

            remote_reading_category = awesome_reading_categories[reading_category['name']]
            reading_type_name_to_reading_category_ids[reading_type].add(remote_reading_category['id'])

    return reading_type_name_to_reading_category_ids


def is_object_different(local_object: dict, remote_object: dict) -> bool:
    """
    Check if the local object has changes that aren't matched on the remote server.

    :param local_object: The local object build using a map function to look like a remote object
    :param remote_object: the data of the remote object
    :return: boolean flag to indicate whether the inspected values are different
    """
    # Check only the values in the local object
    for key, local_value in local_object.items():

        try:
            remote_value = remote_object[key]

        # The remote object doesn't have the expected attribute
        except KeyError:
            LOGGER.error(remote_object)
            raise

        # We found a difference
        if local_value != remote_value:
            return True

    # No differences were found
    return False

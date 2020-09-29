"""
Map Urban Flows assets to Awesome portal objects.
"""

import logging

import objects

LOGGER = logging.getLogger(__name__)


def site_to_location(site: dict) -> dict:
    """Map Urban Flows site to an Awesome portal location"""

    # Get latest activity
    activity = sorted(site['activity'], key=lambda act: act['t0'])[0]

    return objects.Location.new(
        name=str(site['name']),
        lat=float(site['latitude']),
        lon=float(site['longitude']),
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

    # Get location identifier
    location_id = locations[site_name]

    return objects.Sensor.new(
        name=str(sensor['name']),
        location_id=location_id,
        sensor_type_id=1,
        active=bool(sensor['isActive'])
    )


def detector_to_reading_type(detector: dict) -> dict:
    return objects.ReadingType.new(
        name=detector['name'],
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
    for key, value in row.items():
        yield objects.Reading.new(
            sensor_id=awesome_sensor_id,
            reading_type_id=reading_types[key],
            value=value,
            created=time.isoformat(),
        )

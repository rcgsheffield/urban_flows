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


def sensor_to_sensor(sensor: dict, locations: dict) -> dict:
    """Map an Urban Flows sensor to an Awesome sensor"""
    # Get latest site deployment
    pair = sorted(sensor['attachedTo'], key=lambda p: p['from'])[0]
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
        # TODO get real values
        min_value=0,
        max_value=999,
    )


def row_to_readings(row: dict, sensors: dict, awesome_sensors: dict, reading_types) -> iter:
    """
    Convert a row of UFO data into an Awesome portal reading

    :param row: UFO data row
    :param sensors: UFO sensor
    :param reading_types: Awesome reading types
    :return:
    """

    time = row.pop('time')
    uf_sensor_id = row.pop('sensor')
    sensor = sensors[uf_sensor_id]
    awesome_sensor_id = awesome_sensors[sensor['name']]

    LOGGER.debug(sensor)

    del row['site_id']

    # Each row contains several readings
    for key, value in row.items():
        yield objects.Reading.new(
            sensor_id=awesome_sensor_id,
            reading_type_id=reading_types[key],
            value=value,
            created=time,
        )
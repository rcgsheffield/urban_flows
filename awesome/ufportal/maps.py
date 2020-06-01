"""
Map Urban Flows assets to Awesome portal objects.
"""

import logging

import ufportal.objects

LOGGER = logging.getLogger(__name__)


def site_to_location(site: dict) -> dict:
    """Map Urban Flows site to an Awesome portal location"""

    LOGGER.debug(site)

    # Get latest activity
    activity = sorted(site['activity'], key=lambda act: act['t0'])[0]

    return ufportal.objects.Location.new(
        name=str(site['name']),
        lat=float(site['latitude']),
        lon=float(site['longitude']),
        elevation=int(activity['heightAboveSL']),
    )


def sensor_to_sensor(sensor: dict, locations: dict) -> dict:
    # Get latest site deployment
    pair = sorted(sensor['attachedTo'], key=lambda p: p['from'])[0]
    site_name = pair['site']

    # Get location identifier
    location_id = locations[site_name]

    return ufportal.objects.Sensor.new(
        name=str(sensor['name']),
        location_id=location_id,
        sensor_type_id=1,
        active=bool(sensor['isActive'])
    )


def detector_to_reading_type(detector: dict) -> dict:
    return ufportal.objects.ReadingType.new(
        name=detector['name'],
        unit=detector['u'].casefold(),
        min_value=None,
        max_value=None,
    )


def row_to_readings(row: dict, sensors, reading_types) -> iter:
    time = row.pop('time')
    sensor = row.pop('sensor')
    del row['site_id']

    for key, value in row.items():
        yield ufportal.objects.Reading.new(
            sensor_id=sensors[sensor],
            reading_type_id=reading_types[key],
            value=value,
            created=time,
        )

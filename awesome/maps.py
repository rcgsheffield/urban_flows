"""
Map Urban Flows assets to Awesome portal objects.
"""

import logging
import datetime
from typing import List, Mapping

# import pandas

import objects
import settings

LOGGER = logging.getLogger(__name__)


def get_latest_activity(activity: List[dict]) -> dict:
    return sorted(activity, key=lambda act: act['t0'])[0]


def awesome_coordinate(value: float) -> str:
    """Format a float as a ten-decimal-places string"""
    return "{:.10f}".format(value)


def site_to_location(site: dict) -> dict:
    """
    Map Urban Flows site to an Awesome portal location
    """

    # Get latest activity
    activity = get_latest_activity(site['activity'])

    return objects.Location.new(
        name=str(site['name']),
        lat=awesome_coordinate(site['latitude']),
        lon=awesome_coordinate(site['longitude']),
        # Height above sea level in metres
        elevation=int(activity['heightAboveSL']),
        # Street address
        description=str(activity.get('stAdd', '')),
    )


def sensor_latest_deployment(sensor: Mapping) -> dict:
    """
    Get latest site deployment
    """

    # Sort by deployment date (ascending)
    pairs = sorted(sensor['attachedTo'], key=lambda _pair: _pair['from'])

    pair = pairs[0]

    return pair


def sensor_to_sensor(sensor: Mapping, locations: Mapping) -> dict:
    """
    Map an Urban Flows sensor to an Awesome sensor
    """

    pair = sensor_latest_deployment(sensor)
    site_name = pair['site']

    return objects.Sensor.new(
        name=str(sensor['name']),
        location_id=locations[site_name]['id'],
        # TODO map family to sensor type
        sensor_type_id=1,
        active=bool(sensor['isActive'])
    )


def detector_to_reading_type(detector: dict) -> dict:
    return objects.ReadingType.new(
        # Case insensitive
        name=detector['o'].upper(),
        unit=detector['u'].casefold() or 'unit',

        # Absolute maximum values the reading can take.
        # For example, temperature can never go below absolute zero of -273 C
        # TODO configure this on a per-reading-type basis
        min_value=-999999.9,
        max_value=999999.9,
    )


def reading_to_reading(reading: dict, awesome_sensors: Mapping[str, dict],
                       reading_types: Mapping[str, dict]):
    """
    Convert a row of UFO data into multiple Awesome portal readings.

    :param reading: UFO data row
    :param reading_types: Awesome reading types
    :param awesome_sensors: Map Awesome sensor name to identifier
    :return: Generate readings
    """

    # Get detector name e.g. "TRAFF_FLOW" or "MET_AP"
    detector_name = reading['UCD']

    return objects.Reading.new(
        sensor_id=awesome_sensors[reading['sensor.id']]['id'],
        reading_type_id=reading_types[detector_name]['id'],
        value=float(reading['value']),
        created=reading['time'].isoformat(),
    )


def aqi_readings(air_quality_index: Mapping[datetime.datetime, int],
                 aqi_standard_id: int, location_id: int) -> List[
    dict]:
    """
    Convert Air Quality Index values (calculated locally) to AQI Readings for
    the Awesome portal.
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


def reading_type_to_reading_categories(reading_type_groups: list,
                                       awesome_reading_categories: Mapping) -> dict:
    """
    Map reading type names to Awesome reading category identifier

    :param reading_type_groups: The locally configured reading type groups (categories)
    :param awesome_reading_categories: The map of Awesome reading category names to their identifiers
    :return: A map of reading type names to Awesome reading category identifiers
    """
    LOGGER.debug(awesome_reading_categories)

    # Build the mapping
    reading_type_name_to_reading_category_ids = dict()

    # Iterate over locally-defined reading type groups
    for reading_type_group in reading_type_groups:
        for reading_type in reading_type_group['reading_types']:

            # Initialise set
            if reading_type not in reading_type_name_to_reading_category_ids.keys():
                reading_type_name_to_reading_category_ids[reading_type] = set()

            remote_reading_category = awesome_reading_categories[
                reading_type_group['name'].upper()]
            reading_type_name_to_reading_category_ids[reading_type].add(
                remote_reading_category['id'])

    LOGGER.debug(reading_type_name_to_reading_category_ids)
    return reading_type_name_to_reading_category_ids


def is_object_different(local_object: dict, remote_object: dict) -> bool:
    """
    Check if the local object has changes that aren't matched on the remote
    server.

    :param local_object: The local object build using a map function to look
        like a remote object
    :param remote_object: the data of the remote object
    :return: boolean flag to indicate whether the inspected values are
        different
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
            LOGGER.debug('%s: %s != %s', key, repr(local_value),
                         repr(remote_value))
            return True

    # No differences were found
    return False


def family_to_sensor_type(family_name: str,
                          default_rating: float = 0.) -> dict:
    """
    Map a UFO sensor family to an Awesome sensor type

    :param family_name: The family name on the UFO system
    :param default_rating: The quality score value to use if none is configured for that family
    """
    return dict(
        # Convert to upper case so the strings are case insensitive
        name=family_name.upper(),
        manufacturer=family_name,
        # Quality score
        rating=settings.FAMILY_RATING.get(family_name, default_rating)
    )

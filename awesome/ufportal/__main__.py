import argparse
import itertools
import json
import logging
import datetime

import ufportal.assets
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


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true', help='Show more logging information')
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
        LOGGER.debug(site)

        # Convert to Awesome object
        location = ufportal.maps.site_to_location(site)

        try:
            location_id = locations[site['name']]
            loc = ufportal.objects.Location(location_id)
            data = loc.update(session, location)

        # Location doesn't exist on in Awesome database
        except KeyError:

            # Create new location
            data = ufportal.objects.Location.add(session, location)

        LOGGER.debug(data)


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


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Get UFO metadata
    metadata = ufportal.assets.get_metadata()
    sites = metadata['sites'].values()
    sensors = metadata['sensors'].values()
    detectors = {det['name'].upper(): det for det in itertools.chain(*(s['detectors'].values() for s in sensors))}

    with ufportal.http_session.PortalSession() as session:
        # Map key-value pairs to map location name to location identifier
        awesome_sensors = {obj['name']: obj['id'] for obj in ufportal.objects.Sensor.list_iter(session)}
        locations = {obj['name']: obj['id'] for obj in ufportal.objects.Location.list_iter(session)}
        reading_types = {obj['name']: obj['id'] for obj in ufportal.objects.ReadingType.list(session)}
        reading_categories = {obj['name']: obj['id'] for obj in ufportal.objects.ReadingCategory.list(session)}

        # Update Awesome portal to match UFO
        sync_sites(session, sites, locations=locations)
        sync_sensors(session, sensors, awesome_sensors=awesome_sensors, locations=locations)
        sync_reading_types(session, detectors=detectors, reading_types=reading_types)
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


if __name__ == '__main__':
    main()

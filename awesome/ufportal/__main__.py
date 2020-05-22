import logging
import argparse

import ufportal.http_session
import ufportal.assets
import ufportal.maps
import ufportal.awesome_utils
import ufportal.objects

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
API documentation: https://ufapidocs.clients.builtonawesomeness.co.uk/
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true', help='Show more logging information')
    return parser.parse_args()


def add_locations(sites, session):
    for site in sites:
        location = ufportal.maps.site_to_location(site)

        ufportal.objects.Location.store(session, **location)


def add_sensors(sensors, locations, session):
    for sensor in sensors:
        awesome_sensor = ufportal.maps.sensor_to_sensor(sensor, locations)

        ufportal.objects.Sensor.store(session, **awesome_sensor)


def add_reading_categories(session):
    pass


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with ufportal.http_session.PortalSession() as session:
        for cat in ufportal.objects.ReadingCategory.list(session):
            print(cat)
        exit()

    metadata = ufportal.assets.get_metadata()

    with ufportal.http_session.PortalSession() as session:
        add_locations(sites=metadata['sites'], session=session)
        locations = dict(ufportal.awesome_utils.build_location_index(session))
        add_sensors(sensors=metadata['sensors'], locations=locations, session=session)


if __name__ == '__main__':
    main()

import logging
import argparse
import datetime

import ufportal.http_session
from ufportal.objects import Location

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
API documentation: https://ufapidocs.clients.builtonawesomeness.co.uk/
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true', help='Show more logging information')
    return parser.parse_args()


def print_locations(session):
    for location in Location.list(session):
        print(location)


def add_location(session):
    data = {
        "name": "My location",
        "lat": 52.505897,
        "lon": -1.300277,
        "elevation": 100
    }

    print(Location.store(session, obj=data))


def print_location_readings(session, location_id: int):
    loc = Location(location_id)

    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime(2020, 1, 1)
    interval = datetime.timedelta(minutes=60)

    for reading in loc.readings(session, start, end, interval):
        print(reading)


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = ufportal.http_session.PortalSession()

    print_location_readings(session, 963)


if __name__ == '__main__':
    main()

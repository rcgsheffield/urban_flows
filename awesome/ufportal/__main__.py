import logging
import argparse

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


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = ufportal.http_session.PortalSession()

    # for location in Location.list(session):
    #        print(location)

    data = {
        "name": "My location",
        "lat": 52.505897,
        "lon": -1.300277,
        "elevation": 100
    }

    print(Location.store(session, obj=data))


if __name__ == '__main__':
    main()

import logging
import argparse
import random

from pprint import pprint

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


def add_location(site, session):
    location = ufportal.maps.site_to_location(site)

    ufportal.objects.Location.store(session, **location)


def add_locations(metadata, session):
    for site in random.sample(list(metadata['sites'].values()), k=3):
        pprint(site)

        add_location(site, session)


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # metadata = ufportal.assets.get_metadata()

    with ufportal.http_session.PortalSession() as session:
        ufportal.awesome_utils.print_locations(session)


if __name__ == '__main__':
    main()

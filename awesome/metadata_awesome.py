import logging
import json
import argparse
import pathlib

import objects
import http_session
import settings
import utils

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Print object metadata from the Awesome portal API
"""

USAGE = """
python -m show --locations
"""


def get_args():
    """Command-line arguments"""
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='Show more logging information')
    parser.add_argument('-t', '--token', type=pathlib.Path, help='Path of file containing access token',
                        default=settings.DEFAULT_TOKEN_PATH)
    parser.add_argument('-l', '--locations', help="Show locations", action='store_true')
    parser.add_argument('-s', '--sensors', help="Show sensors", action='store_true')
    parser.add_argument('-c', '--sensor_categories', help="Show sensor categories", action='store_true')
    parser.add_argument('-u', '--sensor_types', help="Show sensor types", action='store_true')
    parser.add_argument('-r', '--reading_categories', help="Show reading categories", action='store_true')
    parser.add_argument('-w', '--reading_types', help="Show reading types", action='store_true')

    return parser, parser.parse_args()


def jprint(obj, **kwargs):
    """Print an object in JSON format"""
    print(json.dumps(obj, **kwargs))


def print_objects(session, cls):
    """Print the objects on the Awesome portal"""
    LOGGER.info(cls.__name__)

    # Count items
    n = 0
    for obj in cls.list_iter(session):
        n += 1
        jprint(obj)

    LOGGER.info("Retrieved %s items", n)


def main():
    parser, args = get_args()
    utils.configure_logging(verbose=args.verbose)

    if args.locations:
        cls = objects.Location
    elif args.sensors:
        cls = objects.Sensor
    elif args.sensor_categories:
        cls = objects.SensorCategory
    elif args.sensor_types:
        cls = objects.SensorType
    elif args.reading_categories:
        cls = objects.ReadingCategory
    elif args.reading_types:
        cls = objects.ReadingType
    else:
        parser.print_help()
        exit()

    with http_session.PortalSession(token_path=args.token) as session:
        print_objects(session, cls)


if __name__ == '__main__':
    main()

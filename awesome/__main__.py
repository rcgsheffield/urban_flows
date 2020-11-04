import argparse
import logging
import pathlib

import http_session
import objects
import settings
import sync
import utils

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
API documentation: https://ufapidocs.clients.builtonawesomeness.co.uk/
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true', help='Show more logging information')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--error', type=pathlib.Path, help='Error log file')
    parser.add_argument('-t', '--token', type=pathlib.Path, help='Path of file containing access token',
                        default=settings.DEFAULT_TOKEN_PATH)
    parser.add_argument('-r', '--reading_type_groups', type=pathlib.Path,
                        help="Configuration to group reading types into reading categories",
                        default=settings.DEFAULT_READING_TYPE_GROUPS_FILE)
    parser.add_argument('-a', '--aqi', help="Air quality standards JSON file",
                        default=settings.DEFAULT_AQI_STANDARDS_FILE, type=pathlib.Path)
    return parser.parse_args()


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    reading_type_groups = sync.load_json_objects(args.reading_type_groups)

    # Connect to Awesome portal
    with http_session.PortalSession(token_path=args.token) as session:
        # Get UFO metadata
        sites, families, pairs, sensors, detectors = sync.get_urban_flows_metadata()

        LOGGER.info('Retrieving Awesome portal objects...')

        # Map Awesome object names to object data
        awesome_sensors = sync.build_awesome_object_map(session, objects.Sensor)
        locations = sync.build_awesome_object_map(session, objects.Location)
        reading_types = sync.build_awesome_object_map(session, objects.ReadingType)
        reading_categories = sync.build_awesome_object_map(session, objects.ReadingCategory)

        # TODO skip unchanged objects (don't update if no changes). Perhaps list all Awesome objects and compare to find
        # differences.

        # Upper-case objects names are used so comparisons are case-insensitive

        sync.sync_aqi_standards(session, aqi_standards_file=args.aqi)

        LOGGER.info('Syncing Urban Flows Sites to Awesome Locations...')
        # sync.sync_sites(session, sites, locations=locations)

        LOGGER.info('Syncing sensors...')
        # sync.sync_sensors(session, sensors, awesome_sensors=awesome_sensors, locations=locations)

        LOGGER.info('Syncing reading categories...')
        sync.sync_reading_categories(session, reading_categories=reading_categories,
                                     reading_type_groups=reading_type_groups)

        LOGGER.info('Syncing reading types...')
        sync.sync_reading_types(session, detectors=detectors, reading_types=reading_types,
                                remote_reading_category_ids=reading_categories, reading_type_groups=reading_type_groups)

        # Sync AQI data
        LOGGER.info('Syncing AQI readings...')
        sync.sync_aqi_readings(session, sites=sites, locations=locations)

        # Sync data
        LOGGER.info('Syncing readings...')
        sync.sync_readings(session=session, reading_types=reading_types, sensors=sensors,
                           awesome_sensors=awesome_sensors)


if __name__ == '__main__':
    main()

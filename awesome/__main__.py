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

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show more logging information')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--error', type=pathlib.Path,
                        help='Error log file path')
    parser.add_argument('-i', '--info', type=pathlib.Path,
                        help='Info log file path')
    parser.add_argument('-t', '--token', type=pathlib.Path,
                        help='Path of file containing access token',
                        default=settings.DEFAULT_TOKEN_PATH)

    return parser.parse_args()


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug,
                            error=args.error, info=args.info)

    # Load access token
    with args.token.open() as file:
        token = file.readline().rstrip('\n')

    # Connect to Awesome portal
    with http_session.PortalSession(token=token) as session:
        # Get UFO metadata
        sites, families, pairs, sensors, detectors = sync.get_urban_flows_metadata()

        # Map Awesome object names to object data
        # Upper-case objects names are used so comparisons are case-insensitive
        LOGGER.info('Retrieving Awesome portal objects...')
        awesome_sensors = sync.build_awesome_object_map(session,
                                                        objects.Sensor)
        locations = sync.build_awesome_object_map(session, objects.Location)
        reading_types = sync.build_awesome_object_map(session,
                                                      objects.ReadingType)
        reading_categories = sync.build_awesome_object_map(
            session, objects.ReadingCategory)
        sensor_types = sync.build_awesome_object_map(session,
                                                     objects.SensorType)

        # Sync metadata
        LOGGER.info('Syncing air quality standards...')
        sync.sync_aqi_standards(session)

        LOGGER.info('Syncing families (sensor types)...')
        sync.sync_families(session=session, families=families,
                           sensor_types=sensor_types)

        LOGGER.info('Syncing Urban Flows Sites to Awesome Locations...')
        sync.sync_sites(session, sites, locations=locations)

        LOGGER.info('Syncing sensors...')
        sync.sync_sensors(session=session, sensors=sensors,
                          awesome_sensors=awesome_sensors, locations=locations)

        LOGGER.info('Syncing reading categories...')
        sync.sync_reading_categories(
            session=session, reading_categories=reading_categories,
            reading_type_groups=settings.READING_TYPE_GROUPS)

        LOGGER.info('Syncing reading types...')
        sync.sync_reading_types(
            session=session, detectors=detectors, reading_types=reading_types,
            remote_reading_category_ids=reading_categories,
            reading_type_groups=settings.READING_TYPE_GROUPS)

        # Sync data (readings and AQI analysis)
        LOGGER.info('Syncing readings...')
        sync.sync_readings(session=session, reading_types=reading_types,
                           families=families, awesome_sensors=awesome_sensors)

        LOGGER.info('Syncing AQI readings...')
        sync.sync_aqi_readings(session, sites=sites, locations=locations)


if __name__ == '__main__':
    main()

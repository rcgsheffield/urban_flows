import logging
import argparse
import datetime

import ufportal.http_session
import ufportal.assets
import ufportal.maps
import ufportal.awesome_utils
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


def add_locations(sites, session):
    for site in sites:
        location = ufportal.maps.site_to_location(site)

        ufportal.objects.Location.add(session, **location)


def add_sensors(sensors, locations, session):
    for sensor in sensors:
        awesome_sensor = ufportal.maps.sensor_to_sensor(sensor, locations)

        ufportal.objects.Sensor.add(session, **awesome_sensor)


def add_readings(rows, session):
    for chunk in ufportal.utils.iter_chunks(rows, size=100):
        for row in chunk:
            readings = ufportal.maps.row_to_readings(row)
            ufportal.objects.Reading.store_bulk(session, readings=readings)


def sync_sites(session, sites):
    """Either update or create a new location for each site"""

    location_index = {loc['name']: loc['id'] for loc in ufportal.objects.Location.list_iter(session)}

    for site in sites:
        LOGGER.debug(site)

        # Convert to Awesome object
        location = ufportal.maps.site_to_location(site)

        try:
            location_index[site['name']]
            data = ufportal.objects.Location.update(session, location)

        # Location doesn't exist on in Awesome database
        except KeyError:

            # Create new location
            data = ufportal.objects.Location.add(session, location)

        LOGGER.debug(data)


def sync_sensors(session, sensors):
    """Either update or create a new location for each site"""

    index = {obj['name']: obj['id'] for obj in ufportal.objects.Sensor.list_iter(session)}
    locations = {obj['name']: obj['id'] for obj in ufportal.objects.Location.list_iter(session)}

    for sensor in sensors:
        LOGGER.debug(sensor)

        # Convert to Awesome object
        awe_sensor = ufportal.maps.sensor_to_sensor(sensor, locations)

        try:
            index[sensor['name']]
            data = ufportal.objects.Sensor.update(session, awe_sensor)

        # Doesn't exist on in Awesome database
        except KeyError:
            # Create new
            data = ufportal.objects.Sensor.add(session, awe_sensor)

        LOGGER.debug(data)


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with ufportal.http_session.PortalSession() as session:
        for rt in ufportal.objects.ReadingType.list(session):
            print(rt)
        for rc in ufportal.objects.ReadingCategory.list_iter(session):
            print(rc)

        metadata = ufportal.assets.get_metadata()
        sites = metadata['sites'].values()
        sensors = metadata['sensors'].values()

        sync_sensors(session, sensors)
        sync_sites(session, sites)

    query = dict(
        time_period=[
            datetime.datetime(2020, 3, 2),
            datetime.datetime(2020, 3, 3),
        ],
        site_ids={
            '[SCC]1HBC1:D1',
            'S0045',
            'LD0049',
        },
    )

    # for row in ufportal.ufdex.run(query):


#        print(row)

#


#
# with ufportal.http_session.PortalSession() as session:
#    ufportal.awesome_utils.print_reading_categories(session)
#
#    add_locations(sites=metadata['sites'].values(), session=session)
#    locations = dict(ufportal.awesome_utils.build_location_index(session))
#    add_sensors(sensors=metadata['sensors'].values(), locations=locations, session=session)


if __name__ == '__main__':
    main()

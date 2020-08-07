import argparse
import logging

import http_session
import settings
import utils
from assets import Site, Sensor
from objects import Device, Data

DESCRIPTION = """
Retrieve asset metadata from the Oizom API.
"""

USAGE = """
python -m metadata --sites
python -m metadata --sensors
"""

LOGGER = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--config', help='Configuration file', default=settings.DEFAULT_CONFIG_FILE)
    parser.add_argument('-s', '--sites', action='store_true', help='Print site (location) information')
    parser.add_argument('-n', '--sensors', action='store_true', help='Print sensor (pod) information')
    parser.add_argument('-i', '--status', action='store_true', help='Show status of all devices')
    parser.add_argument('--csv', action='store_true', help='Show CSV headers')
    return parser.parse_args()


def map_device_to_site(device) -> Site:
    """Map Oizom device to an Urban Flows location"""
    return Site(
        site_id=device['deviceId'],
        latitude=device['latitude'],
        longitude=device['longitude'],
        address=device['loc'],
        city=device['city'],
        country=device['country'],
        desc_url=settings.DESC_URL,
    )


def map_device_to_sensor(device, row) -> Sensor:
    """Map Oizom device to an Urban Flows sensor pod"""
    return Sensor(
        sensor_id=device['deviceId'],
        family=settings.FAMILY,
        s_type=device['deviceType'],
        detectors=[dict(name=settings.METRICS[s], unit=settings.UNITS[s])
                   for s in row['payload']['d'].keys() if s != 't'],
        desc_url=settings.DESC_URL,
    )


def print_sites(session):
    """Show site asset metadata"""

    devices = Device.list(session)

    # Get site info
    for device in devices:
        LOGGER.info("Device '%s'", device['deviceId'])

        site = map_device_to_site(device)
        print(site)


def print_sensors(session):
    """Show sensor asset metadata"""

    devices = Device.list(session)

    # Get sensor info
    for device in devices:
        LOGGER.info("Device '%s'", device['deviceId'])

        # Get latest data to get metric names
        row = Data.current_for_device(session, device['deviceId'])
        LOGGER.debug(row)

        sensor = map_device_to_sensor(device, row)
        print(sensor)


def print_status(session):
    """Show current device status"""
    for status in Device.status(session):
        print(status)


def main():
    args = get_args()
    utils.configure_logging(args.verbose)
    session = utils.get_session(args.config)

    if args.status:
        print_status(session)
    elif args.sensors:
        print_sensors(session)
    elif args.csv:
        print(settings.OUTPUT_COLUMNS)
    else:
        print_sites(session)


if __name__ == '__main__':
    main()

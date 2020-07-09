import argparse
import logging

import ufoizom.http_session
import ufoizom.settings
import ufoizom.utils
from ufoizom.assets import Site, Sensor
from ufoizom.objects import Device, Data

DESCRIPTION = """
Retrieve asset metadata from the Oizom API.
"""

USAGE = """
TODO
"""

LOGGER = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--config', help='Configuration file', default=ufoizom.settings.DEFAULT_CONFIG_FILE)
    parser.add_argument('-s', '--status', action='store_true', help='Show status of all devices')
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
        desc_url=ufoizom.settings.DESC_URL,
    )


def map_device_to_sensor(device, row) -> Sensor:
    """Map Oizom device to an Urban Flows sensor pod"""
    return Sensor(
        sensor_id=device['deviceId'],
        family=ufoizom.settings.FAMILY,
        s_type=device['deviceType'],
        detectors=[dict(name=ufoizom.settings.METRICS[s]) for s in row['payload']['d'].keys()],
        desc_url=ufoizom.settings.DESC_URL,
    )


def print_assets(session):
    """Show asset metadata"""
    devices = Device.list(session)

    # Get site info
    for device in devices:
        LOGGER.info("Device '%s'", device['deviceId'])
        LOGGER.debug(device)

        site = map_device_to_site(device)
        print(site)

    # Get sensor info
    for device in devices:
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
    ufoizom.utils.configure_logging(args.verbose)
    session = ufoizom.utils.get_session(args.config)

    if args.status:
        print_status(session)
    else:
        print_assets(session)


if __name__ == '__main__':
    main()

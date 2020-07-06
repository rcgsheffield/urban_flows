import logging
import argparse

import http_session
import assets
import utils
import settings

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Retrieve site and sensor metadata
"""


def get_args():
    """Command-line arguments"""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-s', '--sites', help="Get site metadata", action='store_true')
    parser.add_argument('-n', '--sensors', help="Get sensor metadata", action='store_true')
    parser.add_argument('-v', '--verbose', help="Debug logging level", action='store_true')
    parser.add_argument('-c', '--config', help="Config file", default=settings.DEFAULT_CONFIG_PATH)

    args = parser.parse_args()

    return parser, args


def device_to_site(device: dict) -> assets.Site:
    return assets.Site(
        site_id=device['zNumber'],
        latitude=device['location']['lat'],
        longitude=device['location']['lng'],
        first_date=device['location']['since'][:10],
        country='United Kingdom',
    )


def device_to_sensor(device: dict, slot: str) -> assets.Sensor:
    sensor_id = str(device['zNumber']) + slot
    return assets.Sensor(
        sensor_id=sensor_id,
        family='Zephyr',
        detectors=list(
            dict(name=new) for _, new in settings.FIELD_MAP.items() if new not in {'timestamp', 'sensor'}
        ),
        first_date=device['location']['since'][:10],
    )


def main():
    parser, args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.sites or args.sensors:

        credentials = utils.get_credentials(args.config)
        session = http_session.ZephyrSession(username=credentials['username'], password=credentials['password'])

        for internal_device_id, device in session.devices.items():
            LOGGER.debug("Device ID %s (%s)", internal_device_id, device['zNumber'])

            if args.sites:
                asset = device_to_site(device)
            else:
                for slot in {'A', 'B'}:
                    asset = device_to_sensor(device, slot=slot)

            print(asset)


    else:
        parser.print_help()


if __name__ == '__main__':
    main()

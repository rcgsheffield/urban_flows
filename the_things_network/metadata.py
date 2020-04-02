import logging
import argparse

import ufmetadata.assets

import utils
import objects
import http_session

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Retrieve metadata
"""

USAGE = """
python metadata.py --config my_config_file.cfg
"""


def device_to_site(device) -> ufmetadata.assets.Site:
    site = ufmetadata.assets.Site(
        site_id=device,
    )

    return site


def device_to_sensor(device, family) -> ufmetadata.assets.Sensor:
    sensor = ufmetadata.assets.Sensor(
        sensor_id=device,
        family=family,
        detectors=[
            dict(name='?', unit='?', epsilon='?'),
        ],
    )

    return sensor


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-c', '--config', type=str, required=True, help='Configuration file path')

    return parser.parse_args()


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    config = utils.get_config(args.config)

    session = http_session.StorageSession(**config['session'], access_key=utils.get_access_token())

    for device in objects.Device.list(session=session):
        LOGGER.info("Device: '%s'", device)

        site = device_to_site(device=device)
        site.save()

        sensor = device_to_sensor(device=device, family=session.application_id)
        sensor.save()


if __name__ == '__main__':
    main()

"""
Retrieve metadata
"""

import logging

import utils
import ufmetadata.assets
import api

LOGGER = logging.getLogger(__name__)


def device_to_sensor(device, family) -> ufmetadata.assets.Sensor:
    sensor = ufmetadata.assets.Sensor(
        sensor_id=device,
        family=family,
        detectors=[
            dict(name='?', unit='?', epsilon='?'),
        ],
    )

    return sensor


def main():
    logging.basicConfig(level=logging.INFO)

    session = utils.get_session()

    for device in api.Device.list(session=session):
        LOGGER.info(device)

        sensor = device_to_sensor(device=device, family=session.application_id)

        sensor.save()


if __name__ == '__main__':
    main()

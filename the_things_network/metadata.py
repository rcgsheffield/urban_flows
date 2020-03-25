import logging

import ttn

import utils
import assets

LOGGER = logging.getLogger(__name__)


def device_to_sensor(device) -> assets.Sensor:
    sensor = assets.Sensor(
        sensor_id=device.dev_id,
        family=device.app_id,
        detectors=[
            dict(name='?', unit='?', epsilon='?'),
        ],
    )

    return sensor


def main():
    logging.basicConfig(level=logging.DEBUG)

    config = utils.get_config()

    app_id = config['api']['application_id']
    access_key = utils.get_access_token()

    client = ttn.ApplicationClient(app_id=app_id, access_key=access_key)

    handler = ttn.HandlerClient(app_id=app_id, app_access_key=access_key)

    application = handler.application().get()

    LOGGER.info(application)
    LOGGER.info(application.app_id)
    LOGGER.info(application.payload_format)
    LOGGER.info(application.decoder)
    LOGGER.info(application.encoder)

    for device in client.devices():
        print(device)

        sensor = device_to_sensor(device)

        sensor.save()


if __name__ == '__main__':
    main()

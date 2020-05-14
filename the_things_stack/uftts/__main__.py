import logging
import argparse

import ttn

from ufmetadata.assets import Site, Sensor

USAGE = """
python uftts --app_id <my_app_id> --access_key <my_token>
"""

DESCRIPTION = """
The Things Network

The Things Stack

https://www.thethingsnetwork.org/docs/applications/
https://pypi.org/project/ttn/
https://github.com/TheThingsNetwork/api/blob/master/handler/handler.proto
"""

LOGGER = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument('-a', '--app_id', required=True, help='Application identifier')
    parser.add_argument('-t', '--access_key', help='Authentication token')
    parser.add_argument('-v', '--verbose', action='store_true', help='Logging debug level')

    return parser.parse_args()


def build_device_url(app_id, dev_id):
    return "https://console.thethingsnetwork.org/applications/{app_id}/devices/{dev_id}".format(
        app_id=app_id,
        dev_id=dev_id,
    )


def device_to_site(device, app_id) -> Site:
    return Site(
        site_id=device.dev_id,
        latitude=device.latitude,
        longitude=device.longitude,
        altitude=device.altitude,
        country='United Kingdom',
        desc_url=build_device_url(app_id=app_id, dev_id=device.dev_id),
    )


def device_to_sensor(device, app_id) -> Sensor:
    return Sensor(
        sensor_id=device.dev_id,
        family="The Things Network {}".format(app_id),
        detectors=list(),
        desc_url=build_device_url(app_id=app_id, dev_id=device.dev_id),
    )


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Connect to application API
    handler = ttn.HandlerClient(app_id=args.app_id, app_access_key=args.access_key)
    app = handler.application()

    # List Devices
    # https://github.com/TheThingsNetwork/api/blob/master/handler/handler.proto#L91
    for device in app.devices():
        LOGGER.info("Device '%s'", device.dev_id)

        print(device_to_site(device, app_id=args.app_id))
        print(device_to_sensor(device, app_id=args.app_id))


if __name__ == '__main__':
    main()

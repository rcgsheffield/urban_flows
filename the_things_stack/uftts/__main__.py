import logging
import argparse

import ttn

DESCRIPTION = """
The Things Stack

https://www.thethingsnetwork.org/docs/applications/
https://pypi.org/project/ttn/
https://github.com/TheThingsNetwork/api/blob/master/handler/handler.proto
"""

LOGGER = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-a', '--app_id', required=True, help='Application identifier')
    parser.add_argument('-t', '--access_key', help='Authentication token')
    parser.add_argument('-v', '--verbose', action='store_true', help='Logging debug level')

    return parser.parse_args()


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Connect to application API
    handler = ttn.HandlerClient(app_id=args.app_id, app_access_key=args.access_key)
    app = handler.application()

    # List Devices
    # https://github.com/TheThingsNetwork/api/blob/master/handler/handler.proto#L91
    for device in app.devices():
        print(device.dev_id, device.latitude, device.longitude, sep='\t')


if __name__ == '__main__':
    main()

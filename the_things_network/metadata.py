import configparser
import logging
import getpass

import http_session
import api

LOGGER = logging.getLogger(__name__)


def get_config():
    config = configparser.ConfigParser()
    config.read('the_things_network.cfg')
    return config._sections


def main():
    logging.basicConfig(level=logging.DEBUG)

    config = get_config()
    application_id = config['api']['application_id']
    base_url = config['api']['base_url'].format(application_id=application_id)
    session = http_session.StorageSession(
        base_url=base_url,
        access_key=getpass.getpass('Enter access token: ')
    )

    for device_id in api.Device.list(session):
        device = api.Device(device_id)
        for row in device.query(session, last='7d'):
            print(row)


if __name__ == '__main__':
    main()

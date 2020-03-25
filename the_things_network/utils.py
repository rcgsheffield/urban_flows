import logging
import configparser
import getpass
import csv

import http_session

LOGGER = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = 'the_things_network.cfg'


def get_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    config = configparser.ConfigParser()
    config.read(path)

    return config._sections


def get_access_token() -> str:
    return getpass.getpass('Enter access token: ')


def get_session():
    config = get_config()

    session = http_session.StorageSession(**config['session'])

    return session


def get_headers():
    """Load CSV header labels and data types"""

    config = get_config()

    headers = {label: eval(data_type) for label, data_type in config['csv'].items()}

    LOGGER.info("HEADERS %s", tuple(headers.keys()))

    return headers


def write_csv(path: str, headers: list, rows: iter):
    """Serialise data in CSV format"""
    with open(path, 'w', newline='') as file:
        writer = csv.DictWriter(file, headers)
        writer.writeheader()
        writer.writerows(rows)

        LOGGER.info("Wrote '%s'", file.name)

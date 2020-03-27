import argparse
import logging
import configparser
import getpass
import csv

import http_session

LOGGER = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = 'the_things_network.cfg'


def get_args(*args, **kwargs):
    parser = argparse.ArgumentParser(*args, **kwargs)

    parser.add_argument('-i', '--input', type=str, help="Input JSON file", required=True)
    parser.add_argument('-o', '--output', type=str, help="Output CSV file", required=True)
    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')

    return parser.parse_args()


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


def write_csv(path: str, rows: iter):
    """Serialise data in CSV format"""

    writer = None

    with open(path, 'w', newline='') as file:

        for row in rows:

            # Initialise using headers from the first row
            if not writer:
                writer = csv.DictWriter(file, row.keys())
                writer.writeheader()

            writer.writerow(row)

        LOGGER.info("Wrote '%s'", file.name)

import os.path
import argparse
import logging
import configparser
import getpass
import datetime
import csv

LOGGER = logging.getLogger(__name__)


class UrbanFlowsDialect(csv.Dialect):
    delimiter = '|'
    quotechar = '"'
    escapechar = None
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL


def build_path(root_dir: str, sub_dir: str, date: datetime.date, ext: str) -> str:
    # Directory
    sub_dir = os.path.join(root_dir, sub_dir, *date.isoformat().split('-'))
    os.makedirs(sub_dir, exist_ok=True)

    # File path
    filename = "{}.{}".format(date, ext)
    path = os.path.join(sub_dir, filename)

    return path


def get_args(*args, **kwargs):
    parser = argparse.ArgumentParser(*args, **kwargs)

    parser.add_argument('-i', '--input', type=str, help="Input JSON file", required=True)
    parser.add_argument('-o', '--output', type=str, help="Output CSV file", required=True)
    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-c', '--config', type=str, required=True, help='Configuration file path')

    return parser.parse_args()


def get_config(path: str) -> dict:
    config = configparser.ConfigParser()
    config.read(path)

    return config._sections


def get_access_token() -> str:
    return getpass.getpass('Enter access token: ')


def get_headers(headers: dict) -> dict:
    """Load CSV header labels and data types"""

    headers = {label.casefold(): eval(data_type) for label, data_type in headers.items()}

    LOGGER.info("HEADERS %s", tuple(headers.keys()))

    return headers


def write_csv(path: str, rows: iter, header: bool = True):
    """Serialise data in CSV format"""

    writer = None

    with open(path, 'w', newline='') as file:

        for row in rows:

            # Initialise using headers from the first row
            if not writer:
                writer = csv.DictWriter(file, row.keys(), dialect=UrbanFlowsDialect)

                if header:
                    writer.writeheader()

            writer.writerow(row)

        LOGGER.info("Wrote '%s'", file.name)


def parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()

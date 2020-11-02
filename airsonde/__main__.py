import argparse
import logging
import datetime
import csv
import pathlib

from collections import OrderedDict

import utils
import settings

from objects import Device, Data
from settings import UrbanDialect

DESCRIPTION = """
This is a data pipeline to ingest sensor data from a collection of Environmental Monitoring Solutions (EMS)
AirSonde devices.
"""

USAGE = """
python -m ufoizom -d 2020-02-19 -o test.csv
"""

LOGGER = logging.getLogger(__name__)


def parse_date(date: str) -> datetime.date:
    return datetime.datetime.strptime(date, settings.DATE_FORMAT).date()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-g', '--debug', action='store_true')
    parser.add_argument('-c', '--config', help='Configuration file', default=settings.DEFAULT_CONFIG_FILE,
                        type=pathlib.Path)
    parser.add_argument('-e', '--error', help='Error log file path')
    parser.add_argument('-d', '--date', type=parse_date, required=True, help='YYYY-MM-DD')
    parser.add_argument('-o', '--output', help='Path of output file', required=True, type=pathlib.Path)
    parser.add_argument('-a', '--average', help='Time frequency in seconds', type=int,
                        default=settings.DEFAULT_AVERAGING_TIME)

    return parser.parse_args()


def parse_timestamp(timestamp: int) -> str:
    """Convert Unix timestamp to ISO 8601"""
    t = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    return t.isoformat()


def transform(row: dict) -> dict:
    """Clean a row of data"""
    # Rename metrics
    row = {settings.METRICS[key]: value for key, value in row.items()}

    # Leave timestamp in Unix format
    # row['timestamp'] = parse_timestamp(row['timestamp'])

    # Preserve column order
    return OrderedDict(row)


def write_csv(path: pathlib.Path, rows):
    headers = settings.OUTPUT_COLUMNS
    LOGGER.info('CSV headers %s', headers)
    with path.open('w', newline='\n') as file:
        writer = csv.DictWriter(file, fieldnames=headers, dialect=UrbanDialect)
        writer.writerows(rows)

        LOGGER.info("Wrote '%s'", file.name)


def get_data(session, start, end, average) -> iter:
    # Iterate over all available devices
    for device in Device.list(session):
        LOGGER.info("DEVICE %s", device)

        # Run query against this device
        row_count = 0
        for data in Data.analytics(session, device['deviceId'], start, end, average):
            row_count += 1
            # Build a data row
            row = data['payload']['d'].copy()

            row['sensor'] = device['deviceId']

            yield row

        LOGGER.info("Retrieved %s rows", row_count)


def get_time_range(date: datetime.date) -> tuple:
    """
    Build a time range
    """

    start = datetime.datetime.combine(date, datetime.time.min)

    # Next day
    end = datetime.datetime.combine(date + datetime.timedelta(days=1), datetime.time.min)

    return start, end


def sort(rows: iter, key: str) -> list:
    return sorted(rows, key=lambda row: row[key])


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, error=args.error, debug=args.debug)
    session = utils.get_session(args.config)

    # Time parameters:
    average = datetime.timedelta(seconds=args.average)

    # Run query
    start, end = get_time_range(args.date)
    rows = get_data(session, start, end, average)

    # Clean up
    rows = (transform(row) for row in rows)

    # Sort chronologically
    rows = sort(rows, key='timestamp')

    # Save output file
    write_csv(args.output, rows=rows)


if __name__ == '__main__':
    main()

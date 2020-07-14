import argparse
import logging
import datetime
import csv
import pathlib

from collections import OrderedDict

import ufoizom.http_session
import ufoizom.utils
import ufoizom.settings

from ufoizom.objects import Device, Data

DESCRIPTION = """
This is a data pipeline to ingest sensor data from a collection of Environmental Monitoring Solutions (EMS)
AirSonde devices.
"""

USAGE = """
python -m ufoizom -d 2020-02-19 -o test.csv
"""

LOGGER = logging.getLogger(__name__)


class UrbanDialect(csv.excel):
    """CSV format options"""
    delimiter = '|'


def parse_date(date: str) -> datetime.date:
    return datetime.datetime.strptime(date, ufoizom.settings.DATE_FORMAT).date()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--config', help='Configuration file', default=ufoizom.settings.DEFAULT_CONFIG_FILE)
    parser.add_argument('-d', '--date', type=parse_date, required=True, help='YYYY-MM-DD')
    parser.add_argument('-o', '--output', help='Path of output file', required=True, type=pathlib.Path)
    parser.add_argument('-a', '--averaging', help='Time frequency in seconds', type=int,
                        default=ufoizom.settings.DEFAULT_AVERAGING_TIME)
    return parser.parse_args()


def transform(row: dict) -> dict:
    """Clean a row of data"""
    # Rename metrics
    row = {ufoizom.settings.METRICS[key]: value for key, value in row.items()}

    # Parse Unix timestamp
    row['timestamp'] = datetime.datetime.fromtimestamp(row['timestamp'], tz=datetime.timezone.utc).isoformat()

    # Preserve column order
    return OrderedDict(row)


def write_csv(path: pathlib.Path, rows):
    headers = ufoizom.settings.OUTPUT_COLUMNS
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
        for data in Data.analytics(session, device['deviceId'], start, end, average):
            # Build a data row
            row = data['payload']['d'].copy()

            row['sensor'] = device['deviceId']

            yield row


def main():
    args = get_args()
    ufoizom.utils.configure_logging(args.verbose)
    session = ufoizom.utils.get_session(args.config)

    # Time parameters
    start = datetime.datetime.combine(args.date, datetime.time.min)
    end = datetime.datetime.combine(args.date + datetime.timedelta(days=1), datetime.time.min)
    average = datetime.timedelta(seconds=5 * 60)

    # Run query
    rows = get_data(session, start, end, average)

    # Clean up
    rows = (transform(row) for row in rows)

    # Sort chronologically
    rows = sorted(rows, key=lambda row: row['timestamp'])

    # Save output file
    write_csv(args.output, rows=rows)


if __name__ == '__main__':
    main()

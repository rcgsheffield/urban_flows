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
python . TODO
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
    return parser.parse_args()


def transform(row: dict) -> dict:
    """Clean a row of data"""
    # Rename metrics
    row = {new: row[old] for old, new in ufoizom.settings.METRICS.items()}

    # Parse Unix timestamp
    row['timestamp'] = datetime.datetime.fromtimestamp(row['timestamp'], tz=datetime.timezone.utc).isoformat()

    # Preserve column order
    return OrderedDict(row)


def write_csv(path: pathlib.Path, rows):
    headers = tuple(ufoizom.settings.METRICS.values())
    LOGGER.info('CSV headers %s', headers)
    with path.open('w') as file:
        writer = csv.DictWriter(file, fieldnames=headers, dialect=UrbanDialect)
        writer.writerows(rows)

        LOGGER.info("Wrote '%s'", file.name)


def main():
    args = get_args()
    ufoizom.utils.configure_logging(args.verbose)
    session = ufoizom.utils.get_session(args.config)

    # Time parameters
    start = datetime.datetime.combine(args.date, datetime.time.min)
    end = datetime.datetime.combine(args.date + datetime.timedelta(days=1), datetime.time.min)
    average = datetime.timedelta(seconds=60)

    current = Data.current(session)
    row = current.pop('payload').pop('d')
    LOGGER.info(current)
    row = transform(row)

    write_csv(args.output, rows=[row])

    exit()
    for device in Device.list(session):
        LOGGER.info("DEVICE %s", device)
        for data in Data.analytics(session, device['deviceId'], start, end, average):
            print(data)


if __name__ == '__main__':
    main()

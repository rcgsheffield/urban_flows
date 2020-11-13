import csv
import datetime
import logging
import pathlib
import warnings
from typing import Iterable, Mapping
from collections import OrderedDict

import arrow

import http_session
import settings
import utils
from objects import Instrument, Data
from settings import UrbanDialect

Rows = Iterable[Mapping]

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Aeroqual harvester for the Urban Flows Observatory.
"""

# Ignore Arrow parsing version change warnings
# https://github.com/arrow-py/arrow/issues/612
warnings.simplefilter('ignore', arrow.factory.ArrowParseWarning)


class AeroqualDataArgumentParser(utils.AeroqualArgumentParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('-d', '--date', help='Get data for this day (UTC)', type=date, required=True)
        self.add_argument('-o', '--output', help='Target CSV file path', type=pathlib.Path, required=True)
        self.add_argument('-a', '--averaging', help='period in minutes to average data – minimum 1 minute',
                          type=int, default=settings.DEFAULT_AVERAGING_PERIOD)
        self.add_argument('-j', '--journal', action='store_true', help='Include journal entries')


def date(day: str) -> datetime.datetime:
    """
    Parse ISO date e.g. 2000-01-01
    """
    return datetime.datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)


def parse_timestamp(timestamp: str) -> datetime.datetime:
    """
    Parse timestamp and convert to UTC
    """
    # Extract time zone from string e.g. "(UTC+12:00) Auckland, Wellington" becomes "UTC+12:00"
    tz = timestamp.partition(')')[0][1:]

    return arrow.get(timestamp).replace(tzinfo=tz).to('UTC')


def get_data(session, day: datetime.date, averaging_period: int, include_journal: bool = False) -> Rows:
    start = day
    end = day + datetime.timedelta(days=1)

    for serial_number in Instrument.list(session):
        LOGGER.info("Sensor serial number: %s", serial_number)

        inst = Instrument(serial_number)
        sensor = inst.get(session)

        for key, value in sensor.items():
            LOGGER.info("Sensor '%s' %s: %s", serial_number, key, value)

        data = Data(serial_number)
        rows = data.query(session, start=start, end=end, averagingperiod=averaging_period,
                          includejournal=include_journal)

        for row in rows:
            row = transform(row)

            yield row


def write_csv(path: pathlib.Path, rows: Rows):
    writer = None
    row_count = 0
    with path.open('w', newline='\n') as file:
        for row in rows:
            row_count += 1
            if not writer:
                LOGGER.info("CSV headers %s", row.keys())
                writer = csv.DictWriter(file, fieldnames=row.keys(), dialect=UrbanDialect)

            writer.writerow(row)

    # If no data was written then remove the file
    if not row_count:
        path.unlink()
    else:
        LOGGER.info("Wrote %s rows to '%s'", row_count, file.name)


def transform(row: dict) -> dict:
    row['Time'] = parse_timestamp(row['Time'])

    # Rename columns
    row = OrderedDict(((settings.RENAME_COLUMNS.get(key, key), value) for key, value in row.items()))

    # Select columns (exclude other columns
    row = OrderedDict(((key, row.get(key, '')) for key in settings.SELECTED_COLUMNS))

    return row


def main():
    parser = AeroqualDataArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    session = http_session.AeroqualSession(config_file=args.config)

    rows = get_data(session=session, day=args.date, averaging_period=args.averaging, include_journal=args.journal)
    write_csv(rows=rows, path=args.output)


if __name__ == '__main__':
    main()

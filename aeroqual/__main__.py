import argparse
import datetime
import logging
import csv
import pathlib

from typing import Iterable, Mapping

import http_session
import settings
import utils

from objects import Instrument, Data

Rows = Iterable[Mapping]

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Aeroqual harvester for the Urban Flows Observatory.
"""


class UrbanDialect(csv.excel):
    """
    CSV format for Urban Flows
    """
    delimiter = '|'


def date(day: str) -> datetime.datetime:
    """
    Parse ISO date e.g. 2000-01-01
    """
    return datetime.datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)


def get_args() -> argparse.Namespace:
    """
    Command line arguments
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-g', '--debug', action='store_true')
    parser.add_argument('-e', '--error', help='Error log file path')
    parser.add_argument('-c', '--config', help='Config file', default=str(settings.DEFAULT_CONFIG_FILE))
    parser.add_argument('-d', '--date', help='Get data for this day (UTC)', type=date, required=True)
    parser.add_argument('-o', '--output', help='Target CSV file path', type=pathlib.Path, required=True)
    parser.add_argument('-a', '--averagingperiod', help='period in minutes to average data – minimum 1 minute',
                        type=int, default=settings.DEFAULT_AVERAGING_PERIOD)
    parser.add_argument('-j', '--includejournal', action='store_true', help='Include journal entries')

    return parser.parse_args()


def get_data(session, serial: str, start: datetime.datetime, end: datetime.datetime, averagingperiod: int,
             includejournal: bool = False) -> Rows:
    """
    Fetch instrument data.

    serial = serial number of instrument
    start time = date/time of beginning of required data period (inclusive) – in instrument local time zone, format yyyy-mm-ddThh:mm:ss
    end time = date/time of end of required data period (not inclusive)
    averaging period = period in minutes to average data – minimum 1 minute
    include journal = (optional) whether to include journal entries – true or false
    """
    # Example query:
    # from=2016-01-01T00:00:00&to=2016-01-02T00:00:00&averagingperiod=60&includejournal=false
    params = {
        'from': start.isoformat(),
        'to': end.isoformat(),
        'averagingperiod': averagingperiod,
        'includejournal': includejournal,
    }
    obj = Data(serial)
    body = obj.get(session, params=params)

    data = body.pop('data')

    # Log metadata
    for key, value in body.items():
        LOGGER.info("%s: %s", key, value)

    yield from data


def write_csv(path: pathlib.Path, rows: Rows):
    writer = None
    row_count = 0
    with path.open('w') as file:
        for row in rows:
            row_count += 1
            if not writer:
                LOGGER.info("CSV headers %s", row.keys())
                writer = csv.DictWriter(file, fieldnames=row.keys(), dialect=UrbanDialect)

            writer.writerow(row)

        LOGGER.info("Wrote %s rows to '%s'", row_count, file.name)


def transform(row: dict) -> dict:
    # TODO
    return row


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    session = http_session.AeroqualSession(config_file=args.config)

    LOGGER.debug(session)

    for serial_number in Instrument.list(session):
        LOGGER.info("Sensor serial number: %s", serial_number)

        inst = Instrument(serial_number)
        sensor = inst.get(session)

        start = args.date
        end = args.date + datetime.timedelta(days=1)
        rows = get_data(session, serial_number, start=start, end=end, averagingperiod=args.averagingperiod,
                        includejournal=args.includejournal)
        rows = map(transform, rows)
        write_csv(rows=rows, path=args.output)


if __name__ == '__main__':
    main()

import logging
import csv
import datetime

from collections import OrderedDict

import arrow

LOGGER = logging.getLogger(__name__)


def read_csv(path: str) -> iter:
    """
    Generate rows of input data

    :rtype: iter[dict]
    """
    with open(path) as file:
        reader = csv.DictReader(file)

        LOGGER.info("Reading from '%s'...", file.name)

        yield from reader


def parse(row: dict, data_types: dict) -> iter:
    """Parse input CSV text values into native data types"""

    # Map each column label to a data type
    for label, value in row.items():

        # case-insensitive
        label = label.casefold()

        data_type = data_types[label]

        try:
            value = data_type(value)
        except ValueError:
            # Blank values are set to null
            if not value:
                value = None
            else:
                raise

        yield label, value


def parse_timestamp(timestamp: str) -> datetime.datetime:
    a = arrow.get(timestamp)

    return a.datetime


def transform(row: dict) -> dict:
    # Rename
    row['timestamp'] = row.pop('time')

    # Convert to ISO format
    row['timestamp'] = parse_timestamp(row['timestamp'])

    return row


def to_db(row: dict) -> dict:
    """
    Prepare a row of data to be loaded into the UFO
    """

    del row['raw']

    row = OrderedDict(row)

    # Re-order columns (timestamp, sensor, metrics...)
    for key in ('device_id', 'timestamp'):
        row.move_to_end(key, last=False)

    row['timestamp'] = row['timestamp'].isoformat()

    LOGGER.debug(row)

    return row


def clean(rows: iter, data_types: dict, date: datetime.date) -> iter:
    for row in rows:
        row = dict(parse(row, data_types))

        row = transform(row)

        # Date filter
        if row['timestamp'].date() != date:
            continue

        row = to_db(row)

        yield row

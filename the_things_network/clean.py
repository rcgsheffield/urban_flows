"""
Clean (transform) data
"""

import logging
import argparse
import csv
import datetime

import arrow

import utils

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Parse and clean the CSV data
"""


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
    row['timestamp'] = parse_timestamp(row['timestamp']).isoformat()

    return row


def clean(rows: iter, data_types: dict) -> iter:
    for row in rows:
        row = dict(parse(row, data_types))

        row = transform(row)

        yield row


def main():
    args = utils.get_args(description=DESCRIPTION)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    headers = utils.get_headers()

    # Load, clean and save data
    rows = read_csv(args.input)
    rows = clean(rows, data_types=headers)
    utils.write_csv(args.output, rows=rows)


if __name__ == '__main__':
    main()

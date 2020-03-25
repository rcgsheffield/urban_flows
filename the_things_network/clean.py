"""
Clean (transform) data
"""

import logging
import argparse
import csv
import datetime

import utils

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Parse and clean the CSV data
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-i', '--input', type=str, help="Input CSV file", required=True)
    parser.add_argument('-o', '--output', type=str, help="Output CSV file", required=True)

    return parser.parse_args()


def read_csv(path: str) -> iter:
    """
    Generate rows of input data

    :rtype: iter[dict]
    """
    with open(path) as file:
        reader = csv.DictReader(file)

        LOGGER.info("Reading from '%s'...", file.name)

        yield from reader


def parse(row: dict, data_types: dict) -> dict:
    """Parse input CSV text values into native data types"""

    return {
        key: data_types[key](value) for key, value in row.items()
    }


def transform(row: dict) -> dict:
    # Rename
    row['timestamp'] = row.pop('time')

    # Convert to ISO format
    timestamp = row['timestamp'].replace('Z', '+00:00')
    timestamp = datetime.datetime.fromisoformat(timestamp)
    row['timestamp'] = timestamp.isoformat()

    return row


def clean(rows: iter, data_types: dict) -> iter:
    for row in rows:
        row = parse(row, data_types)

        row = transform(row)

        yield row


def main():
    args = get_args()

    logging.basicConfig(level=logging.INFO)

    headers = utils.get_headers()

    # Load, clean and save data
    rows = read_csv(args.input)
    rows = clean(rows, data_types=headers)
    utils.write_csv(args.output, headers=headers, rows=rows)


if __name__ == '__main__':
    main()

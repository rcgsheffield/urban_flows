"""
Retrieve data
"""

import logging
import argparse
import json
import csv

import utils

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Convert data from JSON format to CSV format.
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-i', '--input', type=str, help="Input JSON file", required=True)
    parser.add_argument('-o', '--output', type=str, help="Output CSV file", required=True)

    return parser.parse_args()


def read_json(path: str) -> list:
    """Parse input JSON"""
    with open(path) as file:
        rows = json.load(file)

        LOGGER.info("Read '%s'", file.name)

    return rows


def main():
    args = get_args()

    logging.basicConfig(level=logging.INFO)

    headers = utils.get_headers()

    # Convert from JSON to CSV
    rows = read_json(args.input)
    utils.write_csv(args.output, headers=headers, rows=rows)


if __name__ == '__main__':
    main()

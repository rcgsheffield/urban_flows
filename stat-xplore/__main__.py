import logging
import csv
import json
import argparse
import pathlib
import itertools
from collections import OrderedDict

from typing import Iterable

import http_session
import objects
import utils

LOGGER = logging.getLogger(__name__)


class UrbanDialect(csv.excel):
    delimiter = '|'


def generate_rows(data: dict) -> Iterable[OrderedDict]:
    """
    Convert data cube into rows of data
    """

    # Get dimension labels
    dim_labels = OrderedDict((field['uri'], field['label']) for field in data['fields'])
    for i, (uri, label) in enumerate(dim_labels.items()):
        LOGGER.info("DIMENSION %s: %s => %s", i, uri, label)

    # Display cube info
    for (uid, cube), measure in zip(data['cubes'].items(), data['measures']):
        LOGGER.info('Cube %s precision %s', uid, cube['precision'])
        LOGGER.info("Measure %s", measure)

    # Get all measures for each cell
    # Iterate over dimensions
    call_values = zip(*(flatten(cube['values']) for cube in data['cubes'].values()))

    # Build dimension labels for each cell
    cell_labels = itertools.product(*(field['items'] for field in data['fields']))

    # Iterate over cells
    for labels, values in zip(cell_labels, call_values):
        # Generate rows of data
        row = OrderedDict()

        # Dimensions
        for label, item in zip(dim_labels.values(), labels):
            row[label] = item['labels'][0]

        # Metric
        for measure, value in zip(data['measures'], values):
            row[measure['label']] = value

        yield row


def flatten(iterable: Iterable) -> Iterable[object]:
    """
    Recursively flatten a nested iterable sequence
    """
    for elem in iterable:
        try:
            yield from flatten(elem)
        except TypeError:
            yield elem


def write_csv(buffer, rows: Iterable[OrderedDict], only_headers: bool = False):
    writer = None

    n_rows = 0
    for row in rows:
        n_rows += 1
        if not writer:
            fieldnames = row.keys()
            writer = csv.DictWriter(buffer, fieldnames=fieldnames, dialect=UrbanDialect)
            LOGGER.info("CSV headers: %s", fieldnames)

            if only_headers:
                print(UrbanDialect.delimiter.join(fieldnames))
                return

        writer.writerow(row)
    LOGGER.info("Wrote %s CSV rows", n_rows)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Define arguments
    parser.add_argument('-k', '--api_key', help='API key')
    parser.add_argument('-v', '--verbose', action='store_true', help='More logging information')
    parser.add_argument('-d', '--debug', action='store_true', help='Extra verbose logging')
    parser.add_argument('-e', '--error', help='Error log file path', default='error.log')
    parser.add_argument('-q', '--query', type=pathlib.Path, help='Open data API query JSON file path', required=True)
    parser.add_argument('-o', '--output', type=pathlib.Path, help='CSV output file path', required=True)
    parser.add_argument('-c', '--csv', action='store_true', help='Show CSV headers')

    return parser.parse_args()


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    session = http_session.StatSession(api_key=args.api_key or utils.load_api_key())

    # Load query
    with args.query.open() as file:
        query = json.load(file)

    # Run query
    data = objects.Table.query(session, **query)
    rows = generate_rows(data)

    # Output
    with args.output.open('w', newline='\n') as file:
        write_csv(file, rows, only_headers=args.csv)


if __name__ == '__main__':
    main()

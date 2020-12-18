import logging
import csv
import json
import argparse
import pathlib
import itertools
from collections import OrderedDict

from typing import Iterable
from pprint import pprint

import http_session
import objects
import settings

LOGGER = logging.getLogger(__name__)


class UrbanDialect(csv.excel):
    delimiter = '|'


def jprint(obj):
    print(json.dumps(obj, indent=2))


def load_api_key(path: pathlib.Path = None) -> str:
    """
    Read API access token from diskn
    """
    path = path or settings.TOKEN_PATH
    with path.open() as file:
        return file.read().strip()


def generate_rows(data: dict) -> Iterable[dict]:
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


def write_csv(buffer, rows: Iterable[OrderedDict]):
    writer = None

    n_rows = 0
    for row in rows:
        n_rows += 1
        if not writer:
            fieldnames = row.keys()
            writer = csv.DictWriter(buffer, fieldnames=fieldnames, dialect=UrbanDialect)
            LOGGER.info("CSV headers: %s", fieldnames)

        writer.writerow(row)
    LOGGER.info("Wrote %s CSV rows", n_rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--api_key', help='API key')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-o', '--output', type=pathlib.Path, help='CSV output path', required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.StatSession(api_key=args.api_key or load_api_key())

    query = dict(
        measures=['str:count:UC_Monthly:V_F_UC_CASELOAD_FULL'],
        dimensions=[
            ['str:field:UC_Monthly:F_UC_DATE:DATE_NAME'],
            ['str:field:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE'],
            ['str:field:UC_Monthly:V_F_UC_CASELOAD_FULL:EMPLOYMENT_CODE'],

        ],
        recodes={
            'str:field:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE': {
                "map": [
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14001028"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000919"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000542"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000667"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000668"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000669"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000876"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000903"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000904"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000920"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000921"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000922"],
                    ["str:value:UC_Monthly:V_F_UC_CASELOAD_FULL:PARLC_CODE:V_C_MASTERGEOG11_PARLC_TO_REGION:E14000923"],
                ],
            }
        },
    )

    data = objects.Table('str:database:UC_Monthly').query(session, **query)
    rows = generate_rows(data)

    with args.output.open('w', newline='\n') as file:
        write_csv(file, rows)


if __name__ == '__main__':
    main()

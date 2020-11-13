"""
CSV data serialisation
"""

import logging
import pathlib
import csv
from typing import Iterable, Dict

import settings

LOGGER = logging.getLogger(__name__)


class UrbanDialect(csv.excel):
    """CSV output format for the Urban Flows Observatory"""
    delimiter = settings.DEFAULT_SEPARATOR


def serialise(rows: Iterable[Dict], path: pathlib.Path, **kwargs):
    """Write to CSV file"""

    fieldnames = settings.OUTPUT_HEADERS

    LOGGER.info("Writing CSV with headers: %s", fieldnames)

    with path.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, dialect=UrbanDialect, **kwargs)

        row_count = 0
        for row in rows:
            writer.writerow(row)

            row_count += 1

    if row_count:
        LOGGER.info("Wrote %s rows to '%s'", row_count, file.name)
    else:
        path.unlink()
        LOGGER.info("Deleted '%s'", file.name)


def print_csv_headers():
    print(UrbanDialect.delimiter.join(settings.OUTPUT_HEADERS))

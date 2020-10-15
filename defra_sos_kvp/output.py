"""
CSV data serialisation
"""

import logging
import csv

import settings

LOGGER = logging.getLogger(__name__)


class UrbanDialect(csv.excel):
    """CSV output format for the Urban Flows Observatory"""
    delimiter = settings.DEFAULT_SEPARATOR


def serialise(rows, path, **kwargs):
    """Write to CSV file"""

    fieldnames = settings.OUTPUT_HEADERS

    LOGGER.info("Writing CSV with headers: %s", fieldnames)

    with open(path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, dialect=UrbanDialect, **kwargs)

        n = 0
        for row in rows:
            # Output timestamp in ISO 8601
            row['timestamp'] = row['timestamp'].isoformat()

            writer.writerow(row)

            n += 1

        LOGGER.info("Wrote %s rows to '%s'", n, file.name)


def print_csv_headers():
    print(UrbanDialect.delimiter.join(settings.OUTPUT_HEADERS))

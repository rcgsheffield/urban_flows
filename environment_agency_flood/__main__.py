import argparse
import csv
import http
import logging
import warnings
import pathlib
from collections import OrderedDict
from typing import Iterable, Dict

import requests

import http_session
import objects
import settings
import utils
import arrow.factory

from settings import UrbanDialect

DESCRIPTION = """
Environment Agency real-time flood monitoring API
https://environment.data.gov.uk/flood-monitoring/doc/reference

Retrieve data from the Environment Agency real-time flood monitoring API and save it to file in CSV format.

Automatically download Environment Agency Flood data for a particular date and particular catchment areas 
and save the source data files to disk.
"""

LOGGER = logging.getLogger(__name__)

warnings.simplefilter("ignore", arrow.factory.ArrowParseWarning)


def get_args() -> argparse.Namespace:
    """Command-line arguments"""

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable debug log mode")
    parser.add_argument('-g', '--debug', action='store_true', help='Debug mode')
    parser.add_argument('-e', '--error', help='Error log file (optional)')
    parser.add_argument('-d', '--date', required=True, type=utils.date, help="ISO UTC date")
    parser.add_argument('-o', '--output', required=True, type=pathlib.Path, help="Output CSV file path")

    args = parser.parse_args()

    return args


def build_new_row():
    """
    Create empty row with the correct number of columns
    """
    return OrderedDict(((key, None) for key in settings.PARAMETER_MAP.values()))


def pivot(rows: iter) -> iter:
    """
    Make one rows for each station, timestamp
    """

    pivoted_rows = dict()

    for row in rows:
        key = row['timestamp'], row['station']

        pivoted_row = pivoted_rows.setdefault(key, build_new_row())

        pivoted_row[row['observed_property']] = row['value']

    # Flatten rows
    for key, values in pivoted_rows.items():
        row = OrderedDict(
            [
                ('timestamp', key[0]),
                ('station', key[1]),
            ]
        )

        for observed_property, value in values.items():
            row[observed_property] = value

        yield row


def sort(rows: iter, key: str = 'timestamp') -> iter:
    """
    Rearrange the rows in ascending order of the specified column
    """
    yield from sorted(rows, key=lambda row: row[key])


def get_data(session, date, station_ids: set) -> iter:
    """
    Download data from the Environment Agency API. First attempts to use the data archive, then use the live data API
    if that fails, which will happen for more recent dates.
    """

    # Attempt to fetch archived data
    try:
        for row in objects.Reading.get_archive(session, date=date):
            yield row

    except requests.HTTPError as http_error:
        # The HTTP error code 404 (not found) means that there is not yet an archived data set for that day
        if http_error.response.status_code != http.HTTPStatus.NOT_FOUND:
            raise

        # Get data from the live API for more recent data sets
        for station_id in station_ids:
            LOGGER.info("Station %s", station_id)

            # Initialise station
            station = objects.Station(station_id)
            station.load(session)

            # Get station data
            for row in station.readings(session, date=date):
                parameter = station.measures[row['measure']]['parameter']
                row['observed_property'] = settings.PARAMETER_MAP[parameter]
                yield row


def serialise(path: pathlib.Path, rows: Iterable[Dict], write_header: bool = False):
    """
    Write the rows of clean data to a file in CSV format.
    """
    headers = settings.HEADERS

    LOGGER.info('CSV headers: %s', headers)

    # Ensure directory structure exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # File output
    with path.open('w', newline='') as file:
        # CSV formatting
        writer = csv.DictWriter(file, fieldnames=headers, dialect=UrbanDialect)

        # Optionally write header row
        if write_header:
            writer.writeheader()

        row_count = 0
        for row in rows:
            row_count += 1
            writer.writerow(row)

    if row_count:
        LOGGER.info("Wrote %s rows to '%s'", row_count, file.name)
    else:
        path.unlink()
        LOGGER.info("Deleted '%s'", file.name)


def transform(rows: iter) -> iter:
    """
    Clean data so that it's ready for ingestion into the UFO database.
    """
    for row in rows:
        # Get the final part of the URL
        # Don't keep the entire URL to minimise disk usage
        row['station'] = row['station'].rpartition('/')[2]

        yield row


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    # Connect to the Environment Agency API
    session = http_session.FloodSession()

    # Retrieve raw data
    rows = get_data(session, date=args.date, station_ids=settings.STATIONS)

    # Only include selected stations
    rows = filter(lambda row: row['station'] in settings.STATIONS, rows)

    # Process data
    rows = sort(pivot(transform(rows)))

    # Output to file
    serialise(args.output, rows=rows)


if __name__ == '__main__':
    main()

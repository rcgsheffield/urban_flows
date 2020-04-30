import argparse
import logging
import requests
import http
import csv

from collections import OrderedDict

import http_session
import objects
import utils
import settings

DESCRIPTION = """
Environment Agency real-time flood monitoring API
https://environment.data.gov.uk/flood-monitoring/doc/reference

Retrieve data from the Environment Agency real-time flood monitoring API and save it to file in CSV format.

Automatically download Environment Agency Flood data for a particular date and particular catchment areas 
and save the source data files to disk.
"""

LOGGER = logging.getLogger(__name__)


class UrbanDialect(csv.excel):
    """CSV output format"""
    delimiter = '|'


def get_args() -> argparse.Namespace:
    """Command-line arguments"""

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-d', '--date', required=True, type=utils.date, help="ISO UTC date")
    parser.add_argument('-o', '--output', required=True, type=str, help="Output CSV file path")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable debug log mode")

    args = parser.parse_args()

    return args


def build_new_row():
    return OrderedDict(((key, None) for key in settings.PARAMETER_MAP.values()))


def pivot(rows: iter) -> iter:
    """Make one rows for each station, timestamp"""

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

            if value is None:
                value = settings.NULL

            row[observed_property] = value

        yield row


def sort(rows: iter) -> iter:
    yield from sorted(rows, key=lambda row: row['timestamp'])


def get_data(session, date) -> iter:
    # Attempt to fetch archived data
    try:
        for row in objects.Reading.get_archive(session, date=date):
            yield row
    # The HTTP error code 404 (not found) means that there is not yet an archived data set for that day
    except requests.HTTPError as http_error:
        if http_error.response.status_code != http.HTTPStatus.NOT_FOUND:
            raise

        # Get data from the live API for more recent data sets
        for station_id in utils.get_stations():
            LOGGER.info("Station %s", station_id)

            station = objects.Station(station_id)
            station.load(session)

            for row in station.readings(session, date=date):
                parameter = station.measures[row['measure']]['parameter']
                row['observed_property'] = settings.PARAMETER_MAP[parameter]
                yield row


def serialise(path, rows):
    headers = ['timestamp', 'station'] + list(settings.PARAMETER_MAP.values())

    LOGGER.info('CSV headers: %s', headers)

    utils.make_dir(path)

    with open(path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers, dialect=UrbanDialect)
        writer.writerows(rows)

        LOGGER.info("Wrote '%s'", file.name)


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.FloodSession()

    serialise(args.output, sort(pivot(get_data(session, date=args.date))))


if __name__ == '__main__':
    main()

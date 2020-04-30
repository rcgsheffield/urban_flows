"""
Utility functions
"""

import datetime
import os.path
import statistics

import arrow

DATE_FORMAT = '%Y-%m-%d'

STATIONS_FILE = 'stations.txt'
MEASURES_FILE = 'measures.txt'


def date(s: str) -> datetime.date:
    return datetime.datetime.strptime(s, DATE_FORMAT).date()


def make_dir(path: str):
    """Build directories for a given path"""
    directory = os.path.dirname(path)

    if directory:
        os.makedirs(directory, exist_ok=True)


def load_lines(path: str) -> iter:
    """Load line from a text file"""
    with open(path) as file:
        # Strip whitespace
        yield from map(str.strip, file.readlines())


def get_stations(path: str = STATIONS_FILE) -> iter:
    return load_lines(path)


def get_measures(path: str = MEASURES_FILE) -> iter:
    return load_lines(path)


def parse_timestamp(timestamp: str) -> str:
    return arrow.get(timestamp).datetime.isoformat()


def parse_value(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return parse_multiple_values(value)


def parse_multiple_values(values: str, sep: str = '|') -> float:
    """Some values look like '0.121|0.130|0.017|-0.033|0.053|0.116|3.390|0.015' for some reason"""
    # Parse all values
    values = map(float, values.split(sep))

    # Take the mean average
    return statistics.mean(values)

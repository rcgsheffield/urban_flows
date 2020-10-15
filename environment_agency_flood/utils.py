"""
Utility functions
"""

import logging
import datetime
import os.path
import statistics

import arrow

from settings import DATE_FORMAT, DEFAULT_STATIONS_FILE, DEFAULT_MEASURES_FILE

LOGGER = logging.getLogger(__name__)


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
        LOGGER.info("Opened '%s'", file.name)

        # Strip whitespace
        for line in file:
            yield line.strip()


def get_stations(path: str = None) -> iter:
    path = path or DEFAULT_STATIONS_FILE
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


def configure_logging(verbose: bool = False, debug: bool = False, error: str = None):
    """
    Configure logging

    :param verbose: Show extra information in logging stream
    :param debug: Debug logging level
    :param error: Error log file path
    """
    fmt = '%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s'
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING, format=fmt)

    if error:
        # Error log file
        handler = logging.FileHandler(filename=error)
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)

        # Capture message on all loggers
        root_logger = logging.getLogger()
        root_logger.handlers.append(handler)

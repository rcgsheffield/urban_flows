"""
Utility functions
"""

import datetime
import os
import logging
import warnings

import arrow
import arrow.factory

import settings

LOGGER = logging.getLogger(__name__)

# Ignore Arrow parsing version change warnings
# https://github.com/arrow-py/arrow/issues/612
warnings.simplefilter('ignore', arrow.factory.ArrowParseWarning)


def within_bounding_box(bounding_box, position: tuple) -> bool:
    """Is a geographical position within the specified area?"""

    latitude, longitude = position

    return (bounding_box[1][0] <= latitude <= bounding_box[0][0]) and (
            bounding_box[0][1] <= longitude <= bounding_box[1][1])


def parse_date(s: str) -> datetime.date:
    t = datetime.datetime.strptime(s, settings.DATE_FORMAT)
    return t.date()


def parse_timestamp(timestamp: str) -> datetime.datetime:
    return arrow.get(timestamp).datetime


def build_path(directory: str, ext: str, date: datetime.date, suffix: str = ''):
    os.makedirs(directory, exist_ok=True)

    if suffix:
        suffix = '_{}'.format(suffix)
    filename = "{date}{suffix}.{ext}".format(date=date.isoformat(), ext=ext, suffix=suffix)

    path = os.path.join(directory, filename)

    return path


def configure_logging(verbose: bool = False, debug: bool = False, error: str = None):
    """
    Configure logging

    :param verbose: Show extra information in logging stream
    :param debug: Debug logging level
    :param error: Error log file path
    """

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING,
                        **settings.LOGGING)

    # TODO subclass formatter to remove line breaks
    # TODO write timestamp as seconds since 1970

    if error:
        # Daily error log files
        handler = logging.FileHandler(filename=error, **settings.ERROR_HANDLER)
        formatter = logging.Formatter(settings.LOGGING.get('format'))
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)

        # Capture message on all loggers
        root_logger = logging.getLogger()
        root_logger.handlers.append(handler)
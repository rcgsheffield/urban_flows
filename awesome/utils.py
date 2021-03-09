import pathlib
import logging
import itertools
import datetime

import arrow

import settings


def parse_timestamp(timestamp: str) -> datetime.datetime:
    """
    Parse ISO 8601/RFC3339 timestamp string to native Python object
    """
    return arrow.get(timestamp).datetime


def iter_chunks(iterable: iter, chunk_size: int) -> iter:
    """
    Iterate over fixed-size chunks of an iterable.

    https://alexwlchan.net/2018/12/iterating-in-fixed-size-chunks/

    :param iterable: a collection or generator
    :param chunk_size: the number of items in each chunk
    :returns: iter[tuple]
    """

    _iterable = iter(iterable)

    while True:
        chunk = tuple(itertools.islice(_iterable, chunk_size))

        # Stop iterating when we reach an empty chunk
        if not chunk:
            break

        yield chunk


def add_handler(filename: pathlib.Path, level: int) -> logging.Handler:
    """
    Add logging handler
    :param filename: output to the file at this path
    :param level: logging verbosity
    """
    # Ensure log file dir exists
    filename = pathlib.Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    # Create log handler to capture records with specified formatting
    handler = logging.FileHandler(filename=str(filename))
    formatter = logging.Formatter(fmt=settings.LOGGING.get('format'))
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # Capture message on all loggers
    root_logger = logging.getLogger()
    root_logger.handlers.append(handler)

    return handler


def configure_logging(verbose: bool = False, debug: bool = False, error: pathlib.Path = None,
                      info: pathlib.Path = None):
    level = logging.DEBUG if debug else logging.INFO if verbose else logging.WARN
    logging.basicConfig(level=level, **settings.LOGGING)

    if error:
        add_handler(filename=error, level=logging.ERROR)

    if info:
        add_handler(filename=info, level=level)

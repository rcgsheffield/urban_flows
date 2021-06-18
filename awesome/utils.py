import pathlib
import logging
import itertools
import datetime
import sys

import arrow

import settings

LOGGER = logging.getLogger(__name__)


def now() -> datetime.datetime:
    """
    Current timestamp with time zone info
    """
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


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


def configure_logging(verbose: bool = False, debug: bool = False,
                      error: pathlib.Path = None, info: pathlib.Path = None):
    level = logging.DEBUG if debug else logging.INFO if verbose else logging.WARN
    logging.basicConfig(level=level, **settings.LOGGING)

    if error:
        add_handler(filename=error, level=logging.ERROR)

    if info:
        add_handler(filename=info, level=level)

    # Log uncaught exceptions
    sys.excepthook = handle_exception


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Log exceptions
    """
    # Origin: https://stackoverflow.com/a/16993115/8634200

    LOGGER.exception("Uncaught exception",
                     exc_info=(exc_type, exc_value, exc_traceback))


def load_file(path: pathlib.Path) -> str:
    with pathlib.Path(path).open() as file:
        return file.readline().rstrip('\n')

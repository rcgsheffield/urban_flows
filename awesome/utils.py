import pathlib
import logging
import itertools

import settings


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


def configure_logging(verbose: bool = False, debug: bool = False, error: pathlib.Path = None):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO if verbose else logging.WARN,
                        **settings.LOGGING)

    if error:
        # Daily error log files
        handler = logging.FileHandler(filename=str(error))
        formatter = logging.Formatter()
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)

        # Capture message on all loggers
        root_logger = logging.getLogger()
        root_logger.handlers.append(handler)

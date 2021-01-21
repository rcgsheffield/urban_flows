import json
import pathlib
import sys
import logging

import settings

LOGGER = logging.getLogger(__name__)


def load_api_key(path: pathlib.Path = None) -> str:
    """
    Read API access token from diskn
    """
    path = pathlib.Path(path)
    with path.open() as file:
        return file.read().strip()


def jprint(obj):
    print(json.dumps(obj, indent=2))


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Log exceptions
    """
    # Origin: https://stackoverflow.com/a/16993115/8634200

    # Don't log keyboard interrupts
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    LOGGER.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def configure_logging(verbose: bool = False, debug: bool = False, error: str = None):
    """
    Configure logging

    :param verbose: Show extra information in logging stream
    :param debug: Debug logging level
    :param error: Error log file path
    """

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING,
                        **settings.LOGGING)

    if error:
        # Error log file
        handler = logging.FileHandler(filename=error)
        formatter = logging.Formatter(fmt=settings.LOGGING.get('format'))
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)

        # Capture message on all loggers
        root_logger = logging.getLogger()
        root_logger.handlers.append(handler)

    # Log any uncaught exceptions
    sys.excepthook = handle_exception

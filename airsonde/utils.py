import logging
import configparser
import pathlib

import http_session
import settings


def load_config(path: pathlib.Path) -> configparser.ConfigParser:
    path = pathlib.Path(path)
    config = configparser.ConfigParser()

    with path.open() as file:
        config.read_file(file)

    return config


def get_session(config_file: pathlib.Path) -> http_session.OizumSession:
    config = load_config(config_file)
    return http_session.OizumSession(client_id=config['credentials']['client_id'],
                                     client_secret=config['credentials']['client_secret'])


def configure_logging(verbose: bool = False, error: str = None, debug: bool = False):
    """
        Configure logging

        :param verbose: Show extra information in logging stream
        :param debug: Debug logging level
        :param error: Error log file path
        """

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO if verbose else logging.WARNING,
                        **settings.LOGGING)

    if error:
        # Daily error log files
        handler = logging.handlers.TimedRotatingFileHandler(filename=error, **settings.ERROR_HANDLER)
        formatter = logging.Formatter(settings.LOGGING.get('format'))
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)

        # Capture message on all loggers
        root_logger = logging.getLogger()
        root_logger.handlers.append(handler)

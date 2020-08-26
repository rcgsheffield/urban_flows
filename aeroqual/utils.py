import argparse
import logging

import settings


class AeroqualArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_argument('-v', '--verbose', action='store_true')
        self.add_argument('-g', '--debug', action='store_true')
        self.add_argument('-e', '--error', help='Error log file path')
        self.add_argument('-c', '--config', help='Config file', default=str(settings.DEFAULT_CONFIG_FILE))


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
        # Daily error log files
        handler = logging.FileHandler(filename=error)
        formatter = logging.Formatter(settings.LOGGING.get('format'))
        handler.setFormatter(formatter)
        handler.setLevel(logging.ERROR)

        # Capture message on all loggers
        root_logger = logging.getLogger()
        root_logger.handlers.append(handler)

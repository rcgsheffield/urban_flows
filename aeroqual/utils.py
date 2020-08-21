import logging

import settings


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

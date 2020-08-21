import logging
import argparse

import settings
import utils
import http_session

from objects import Instrument

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Aeroqual harvester for the Urban Flows Observatory.
"""


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--error', help='Error log file path')
    parser.add_argument('-c', '--config', help='Config file', default=str(settings.DEFAULT_CONFIG_FILE))

    return parser.parse_args()


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    session = http_session.AeroqualSession(config_file=args.config)

    LOGGER.debug(session)

    for x in Instrument.list(session):
        print(x)


if __name__ == '__main__':
    main()

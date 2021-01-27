import logging
import argparse

import objects
import http_session
import utils

LOGGER = logging.getLogger(__name__)


def get_args():
    """
    Command-line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--profiles', action='store_true', help='List profiles')
    return parser, parser.parse_args()


def main():
    parser, args = get_args()
    logging.basicConfig()
    with http_session.FingertipsSession() as session:
        if args.profiles:
            utils.jprint(objects.Profile.list(session))
        else:
            parser.print_help()


if __name__ == '__main__':
    main()

import logging
import argparse
import pathlib
from pprint import pprint

import http_session
import objects
import settings


def load_api_key(path: pathlib.Path = None) -> str:
    """
    Read API access token from disk
    """
    path = path or settings.TOKEN_PATH
    with path.open() as file:
        return file.read().strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--api_key', help='API key')
    parser.add_argument('-v', '--verbose')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.StatSession(api_key=args.api_key or load_api_key())

    pprint(objects.Schema('str:folder:fuc').get(session))
    pprint(objects.Table('str:database:UC_Starts').get(session))


if __name__ == '__main__':
    main()

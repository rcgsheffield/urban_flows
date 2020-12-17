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
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.StatSession(api_key=args.api_key or load_api_key())

    # pprint(objects.Schema.list(session))
    # pprint(objects.Schema('str:folder:fuc').get(session))
    # pprint(objects.Schema('str:database:UC_Monthly').get(session))
    data = objects.Table('str:database:UC_Monthly').query(
        session,
        measures=['str:count:UC_Monthly:V_F_UC_CASELOAD_FULL'],
        dimensions=[['str:field:UC_Monthly:F_UC_DATE:DATE_NAME']],
    )
    pprint(data)


if __name__ == '__main__':
    main()

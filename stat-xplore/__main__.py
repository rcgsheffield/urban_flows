import logging
import argparse
from pprint import pprint

import http_session
import objects


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--api_key', help='API key', required=True)
    parser.add_argument('-v', '--verbose')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.StatSession(api_key=args.api_key)

    # pprint(objects.Schema('str:folder:fuc').get(session))
    pprint(objects.Table('str:database:UC_Starts').get(session))


if __name__ == '__main__':
    main()

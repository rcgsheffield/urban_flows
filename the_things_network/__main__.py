"""
Retrieve data
"""

import logging
import argparse
import json

import utils
import transform
import http_session

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Download data from The Things Network Data Storage integration via its web API.
"""

USAGE = """
TODO
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)

    parser.add_argument('-o', '--output', default='todb', type=str, help="Output directory")
    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-c', '--config', type=str, required=True, help='Configuration file path')
    parser.add_argument('-d', '--date', type=utils.parse_date, required=True, help='Temporal filter YYYY-MM-DD')
    parser.add_argument('-r', '--raw', default='raw', type=str, help="Raw data output directory")
    parser.add_argument('-f', '--header', default=False, type=bool, help="Write CSV field header row")

    return parser.parse_args()


def download_data(session, path: str) -> str:
    data = session.query_raw(last='7d').text

    # Serialise
    with open(path, 'w') as file:
        file.write(data)

        LOGGER.info("Wrote '%s'", file.name)

    return data


def parse_data(data: str) -> list:
    return json.loads(data)


def main():
    args = get_args()
    config = utils.get_config(args.config)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.StorageSession(**config['session'], access_key=utils.get_access_token())

    root_dir = config['data']['root_dir']

    raw_path = utils.build_path(root_dir=root_dir, sub_dir=args.raw, date=args.date, ext='json')
    data = download_data(session, path=raw_path)

    rows = parse_data(data)

    LOGGER.info("Retrieved %s rows", len(rows))

    headers = utils.get_headers(config['fields'])
    rows = transform.clean(rows, data_types=headers)

    output_path = utils.build_path(root_dir=root_dir, sub_dir=args.output, date=args.date, ext='csv')
    utils.write_csv(path=output_path, rows=rows, header=args.header)


if __name__ == '__main__':
    main()

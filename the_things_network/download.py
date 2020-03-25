"""
Retrieve data
"""

import logging
import argparse

import utils

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Download data from The Things Network Data Storage integration via its web API.
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-o', '--output', type=str, help="Output JSON file", required=True)

    return parser.parse_args()


def main():
    args = get_args()

    logging.basicConfig(level=logging.DEBUG)

    session = utils.get_session()

    # Download
    data = session.query_raw(last='7d').content

    # Serialise
    with open(args.output, 'wb') as file:
        file.write(data)

        LOGGER.info("Wrote '%s'", file.name)


if __name__ == '__main__':
    main()

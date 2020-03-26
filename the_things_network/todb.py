import logging
import argparse

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Parse and clean the CSV data
"""


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-i', '--input', type=str, help="Input CSV file", required=True)
    parser.add_argument('-o', '--output', type=str, help="Output CSV file", required=True)

    return parser.parse_args()


def main():
    args = get_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)


if __name__ == '__main__':
    main()

import logging
import json

import utils

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Convert data from JSON format to CSV format.
"""


def read_json(path: str) -> list:
    """Parse input JSON"""
    with open(path) as file:
        rows = json.load(file)

        LOGGER.info("Read '%s'", file.name)

    return rows


def main():
    args = utils.get_args(description=DESCRIPTION)

    logging.basicConfig(level=logging.INFO)

    # Convert from JSON to CSV
    rows = read_json(args.input)
    utils.write_csv(args.output, rows=rows)


if __name__ == '__main__':
    main()

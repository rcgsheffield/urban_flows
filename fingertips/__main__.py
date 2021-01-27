import logging
import argparse
import itertools

import http_session
import objects
import utils

DESCRIPTION = """
Public Health England (PHE) Fingertips harvester
"""

LOGGER = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='More logging information')
    parser.add_argument('-d', '--debug', action='store_true', help='Extra verbose logging')
    parser.add_argument('-e', '--error', help='Error log file path', default='error.log')

    # Data filters
    parser.add_argument('-p', '--profile_id', type=int, help='National health profile identifier', required=True)
    parser.add_argument('-i', '--indicator_id', type=int, help='Indicator identifier', required=True)
    parser.add_argument('-a', '--area_type_id', type=int, help='Area type identifier', required=True)
    parser.add_argument('-r', '--parent_area_type_id', type=int, help='Parent area type identifier', required=True)
    parser.add_argument('-c', '--area_code', type=str, help='Area code', required=False)

    return parser.parse_args()


def row_filter(row: dict, args: argparse.Namespace) -> bool:
    # Filter by area code (if specified)
    if args.area_code:
        if row['Area Code'] != args.area_code:
            return False

    return True


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)
    session = http_session.FingertipsSession()

    # Get data
    profile = objects.Profile(args.profile_id)
    lines = profile.data(session, child_area_type_id=args.area_type_id, parent_area_type_id=args.parent_area_type_id)
    rows = utils.parse_csv(lines)
    rows = (row for row in rows if row_filter(row, args=args))

    utils.write_csv(rows)


if __name__ == '__main__':
    main()

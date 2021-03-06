import logging
import argparse
import pathlib
import sys

import http_session
import objects
import utils

DESCRIPTION = """
Public Health England (PHE) Fingertips harvester
"""

LOGGER = logging.getLogger(__name__)


def path(s: str) -> pathlib.Path:
    return pathlib.Path(s)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true', help='More logging information')
    parser.add_argument('-d', '--debug', action='store_true', help='Extra verbose logging')
    parser.add_argument('-e', '--error', help='Error log file path', default='error.log')
    parser.add_argument('-o', '--output', type=path, help='Output CSV file path')
    parser.add_argument('-w', '--write_header', action='store_true', help='Write CSV header row')

    # Data filters
    parser.add_argument('-p', '--profile_id', type=int, help='National health profile identifier', required=False)
    parser.add_argument('-i', '--indicator_id', type=int, help='Indicator identifier', required=False)
    parser.add_argument('-a', '--area_type_id', type=int, help='Area type identifier', required=True)
    parser.add_argument('-r', '--parent_area_type_id', type=int, help='Parent area type identifier', required=True)
    parser.add_argument('-c', '--area_code', type=str, help='Area code', required=False)

    return parser.parse_args()


def row_filter(row: dict, args: argparse.Namespace) -> bool:
    # Filter by area code (if specified)
    if args.area_code:
        try:
            if row['Area Code'] != args.area_code:
                return False
        except KeyError:
            LOGGER.error(row)
            raise
    return True


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)
    session = http_session.FingertipsSession()

    # Get data
    if args.indicator_id:
        lines = objects.Data.by_indicator_id(session, indicator_ids={args.indicator_id},
                                             child_area_type_id=args.area_type_id,
                                             parent_area_type_id=args.parent_area_type_id)

    elif args.profile_id:
        lines = objects.Data.by_profile_id(session, child_area_type_id=args.area_type_id,
                                           parent_area_type_id=args.parent_area_type_id, profile_id=args.profile_id)
    else:
        raise argparse.ArgumentError(None, 'Either indicator_id or profile_id are required')

    rows = utils.parse_csv(lines)
    # Filter
    rows = (row for row in rows if row_filter(row, args=args))

    # Write to file (or to screen)
    buffer = args.output.open('w', newline='\n') if args.output else sys.stdout
    utils.write_csv(rows, buffer=buffer, write_header=args.write_header)


if __name__ == '__main__':
    main()

import argparse
import logging
from typing import Union

import http_session
import objects
import utils

LOGGER = logging.getLogger(__name__)


def get_args():
    """
    Command-line arguments
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--profiles', action='store_true', help='List profiles')
    parser.add_argument('-a', '--area_types', action='store_true', help='List area types')
    parser.add_argument('-t', '--parent_area_types', action='store_true', help='List parent area types')
    parser.add_argument('-i', '--profile_id', type=int, help='Health profile identifier')
    parser.add_argument('-s', '--search_indicators', type=str, help='Words can be combined with AND, OR')
    parser.add_argument('-n', '--indicator_id', type=int, help='Show indicator details')

    return parser, parser.parse_args()


def get_metadata(args: argparse.Namespace, session) -> Union[list, dict]:
    # List all profiles
    if args.profiles:
        result = objects.Profile.list(session)

    # One profile
    elif args.profile_id:
        result = objects.Profile(args.profile_id).get(session)

    # Area types
    elif args.area_types or args.parent_area_types:
        profile = objects.Profile(args.profile_id)
        if args.parent_area_types:
            result = profile.parent_area_types(session)
        else:
            result = profile.area_types(session)

    elif args.search_indicators:
        result = objects.Indicator.search_list(session, args.search_indicators)

    elif args.indicator_id:
        key = str(args.indicator_id)
        result = objects.Indicator(args.indicator_id).get(session)[key]
        result['profiles'] = objects.Profile.containing_indicators(session, indicator_ids={args.indicator_id})[key]

    else:
        raise argparse.ArgumentError(None, 'No option selected')

    return result


def main():
    """
    Get the requested metadata objects and print to screen
    """
    parser, args = get_args()
    logging.basicConfig()
    session = http_session.FingertipsSession()
    try:
        result = get_metadata(args, session)
        utils.jprint(result)
    except argparse.ArgumentError:
        parser.print_help()


if __name__ == '__main__':
    main()

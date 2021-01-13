import logging
import argparse

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

    return parser.parse_args()


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)
    session = http_session.FingertipsSession()

    # utils.jprint(objects.AreaType.list(session))

    # pprint(objects.Data.list(session))

    # for profile in objects.Profile.list(session):
    #     utils.jprint(profile)

    # Profile ID 100 "Wider Impacts of COVID-19 on Health"
    # GroupMetadata 1938133359 "Impact on mortality"

    # profile = objects.Profile(100)
    # utils.jprint(profile.get(session))
    #
    # group = objects.Group(1938133359)
    # utils.jprint(group.get(session))

    # indicators = group.indicators(session)
    # utils.jprint(indicators)

    # Healthy life expectancy at birth
    indicator = objects.Indicator(90362)
    utils.jprint(indicator.get(session))


if __name__ == '__main__':
    main()

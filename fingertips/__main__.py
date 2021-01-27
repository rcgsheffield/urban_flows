import logging
import argparse
import json

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

    profile = objects.Profile(100)
    LOGGER.info(json.dumps(profile.get(session)))

    # group = objects.Group(1938133359)
    # utils.jprint(group.get(session))

    # indicators = group.indicators(session)

    # Indicator 90362 "Healthy life expectancy at birth" (under profile 100)
    indicator = objects.Indicator(90362)
    LOGGER.info("Indicator %s", json.dumps(indicator.get(session)))

    # List area types
    # for area_type in profile.area_types(session):
    # if 'county' in area_type['Name'].casefold():
    # utils.jprint(area_type)

    # Area type 6 "Region"
    # Area type 201 "District & UA (4/19-3/20)" i.e. "Lower tier local authorities (4/19 - 3/20)"
    # Area type 15 = England
    # utils.jprint(objects.AreaType(6).get(session))

    # List areas of type Distict
    # utils.jprint(objects.Area.list(session, area_type_id=201))
    # Sheffield area ID 170
    # {"AreaTypeId": 170,"Short": "Sheffield","Name": "Sheffield","Code": "E08000019"}

    # Get that sweet, sweet data
    data = indicator.data(session, child_area_type_id=6, parent_area_type_id=15, profile_id=100)
    for line in data:
        print(line)


if __name__ == '__main__':
    main()

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

PROFILE_ID = 26


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

    # utils.jprint(objects.AreaCategory.list(session))

    # utils.jprint(objects.AreaType.list(session))

    # pprint(objects.Data.list(session))

    # Profile ID 100 "Wider Impacts of COVID-19 on Health"
    # 26 Local Authority Health Profiles
    # GroupMetadata 1938133359 "Impact on mortality"
    profile = objects.Profile(PROFILE_ID)
    profile_data = profile.get(session)
    LOGGER.info("Profile %s %s", profile.identifier, profile_data['Name'])

    for parent_area_type in profile.parent_area_types(session):
        LOGGER.info("Parent area type: %s %s", parent_area_type['Id'], parent_area_type['Name'])

    for area_type in profile.area_types(session):
        LOGGER.info("Area type: %s %s", area_type['Id'], area_type['Name'])

    for x in profile.data(session, child_area_type_id=201, parent_area_type_id=6):
        print(x)

    #
    # Iterate over profiles
    # for profile in objects.Profile.list(session):
    #     LOGGER.info("Profile %s %s", profile['Id'], profile['Name'])
    #
    #     # Get areas in this profile
    #     profile = objects.Profile(profile['Id'])
    #     parent_area_types = profile.parent_area_types(session)
    #     area_types = profile.area_types(session)
    #
    #     for parent_area_type, area_type in itertools.product(parent_area_types, area_types):
    #         LOGGER.info("Parent area type: %s %s", parent_area_type['Id'], parent_area_type['Name'])
    #         LOGGER.info("Area type: %s %s", area_type['Id'], area_type['Name'])
    #         for x in profile.data(session, child_area_type_id=area_type['Id'],
    #                               parent_area_type_id=parent_area_type['Id']):
    #             print(x)
    #         exit()

    # profile_groups = objects.ProfileGroup.list(session, group_ids=profile_data['GroupIds'])
    # utils.jprint(profile_groups)
    # exit()

    # group = objects.Group(1938133359)
    # utils.jprint(group.get(session))

    # indicators = group.indicators(session)

    # Indicator 90362 "Healthy life expectancy at birth" (under profile 100)
    # indicator = objects.Indicator(90362)
    # LOGGER.info("Indicator %s", json.dumps(indicator.get(session)))

    # List area types
    # for area_type in profile.area_types(session):
    #     utils.jprint(area_type)

    # Area type 6 "Region"
    # Area type 201 "District & UA (4/19-3/20)" i.e. "Lower tier local authorities (4/19 - 3/20)"
    # Area type 15 = England
    # utils.jprint(objects.AreaType(6).get(session))

    # List areas of type Distict
    # utils.jprint(objects.Area.list(session, area_type_id=201))
    # Sheffield area ID 170
    # {"AreaTypeId": 170,"Short": "Sheffield","Name": "Sheffield","Code": "E08000019"}

    # Get that sweet, sweet data
    # England by region (works!)
    # data = indicator.data(session, child_area_type_id=6, parent_area_type_id=15, profile_id=100)
    # data = indicator.data(session, child_area_type_id=201, parent_area_type_id=6, profile_id=PROFILE_ID)
    # for line in data:
    #     utils.jprint(line, indent=None)


if __name__ == '__main__':
    main()

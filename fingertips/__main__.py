"""
Fingertips harvester
"""

from pprint import pprint

import http_session
import objects


def main():
    session = http_session.FingertipsSession()

    pprint(objects.AreaType.list(session))

    # pprint(objects.Data.list(session))

    # data = objects.Profile.list(session)
    # for profile in data:
    #     if 'health' in profile['Name'].casefold():
    #         pprint(profile)


if __name__ == '__main__':
    main()

import logging
from getpass import getpass
from pprint import pprint

import http_session
import maps
import settings
import sync
import objects

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    session = http_session.PortalSession(token=getpass())

    reading_categories = sync.build_awesome_object_map(
        session, objects.ReadingCategory)

    pprint(reading_categories)

    x = maps.reading_type_to_reading_categories(
        reading_type_groups=settings.READING_TYPE_GROUPS,
        awesome_reading_categories=reading_categories)

    pprint(x)

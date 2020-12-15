from pprint import pprint

import objects
import sync
import http_session

session = http_session.PortalSession()
reading_types = sync.build_awesome_object_map(session, objects.ReadingType)

pprint(reading_types)

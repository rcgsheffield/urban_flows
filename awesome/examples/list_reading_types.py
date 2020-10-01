import http_session
import sync
import objects

from pprint import pprint

session = http_session.PortalSession()

reading_types = sync.build_awesome_object_map(session, objects.ReadingType)

pprint(reading_types)

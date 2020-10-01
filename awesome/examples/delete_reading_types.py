import http_session
import objects

from pprint import pprint

session = http_session.PortalSession()

for reading_type in objects.ReadingType.list_iter(session):
    pprint(reading_type)

    obj = objects.ReadingType(reading_type['id'])
    obj.delete(session)

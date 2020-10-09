import http_session

from objects import AQIStandard

from pprint import pprint

session = http_session.PortalSession()

for obj_data in AQIStandard.list_iter(session):
    pprint(obj_data)

    obj = AQIStandard(obj_data['id'])
    obj.delete(session)

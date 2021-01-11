import http_session

from objects import Location

if __name__ == '__main__':
    session = http_session.PortalSession()

    for location in Location.list_iter(session):
        print(location)

        # More detailed info (including sensors)
        # loc = Location(location['id'])
        # loc_data = loc.get(session)
        # print(loc_data)

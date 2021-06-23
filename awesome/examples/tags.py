import logging
import objects
import http_session
import getpass

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    session = http_session.PortalSession(getpass.getpass('token: '))
    location = objects.Location(776)

    print(location.tags(session))
    print(location.add_tag(session, tag='test'))
    for tag in location.tags(session):
        print(tag)
        location.delete_tag(session, tag_id=tag['id'])
    print(location.tags(session))

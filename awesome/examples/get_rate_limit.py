import logging

import http_session
import objects

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    session = http_session.PortalSession()

    while True:
        loc = objects.Location(776)
        loc.get(session)

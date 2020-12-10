import logging
import http_session
import objects

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    session = http_session.CKANSession()

    pack = objects.Package('key-stage-4-performance-2020')

    print(pack.get(session))

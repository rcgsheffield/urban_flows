import logging
from typing import List

import http_session
import objects

LOGGER = logging.getLogger(__name__)


def search_packages(session, query: str) -> List[dict]:
    """
    :param query: SOLR query string
    """
    return objects.Package.search(session, q=query)['results']


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    session = http_session.CKANSession()

    for package in search_packages(session, 'key-stage-4'):
        print(package['name'])

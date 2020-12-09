import logging

import objects

LOGGER = logging.getLogger(__name__)


def search_data_sets(session, search: str):
    """
    Discover available datasets
    """

    for key_family in objects.KeyFamily.list(session, search=search):
        LOGGER.debug(key_family)

        print(key_family['id'], key_family['name']['value'])

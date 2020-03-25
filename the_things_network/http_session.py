import logging
import urllib.parse
import requests
import json
import http

import utils

LOGGER = logging.getLogger(__name__)


class StorageSession(requests.Session):
    """
    Thing Things Network Data Storage API HTTP Session

    https://www.thethingsnetwork.org/docs/applications/storage/api.html
    """

    def __init__(self):
        super().__init__()

        config = utils.get_config()

        self.application_id = config['api']['application_id']
        self.base_url = config['api']['base_url'].format(application_id=self.application_id)
        self.access_key = utils.get_access_token()

        self.headers.update(self.extra_headers)

    @property
    def extra_headers(self):
        return {
            'Authorization': "key {access_key}".format(access_key=self.access_key),
        }

    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)

        for key, value in response.headers.items():
            LOGGER.debug("RESPONSE %s: %s", key, value)

        response.raise_for_status()
        return response

    def call(self, endpoint: str, **kwargs) -> list:
        url = urllib.parse.urljoin(self.base_url, endpoint)

        response = self.get(url, **kwargs)

        try:
            data = response.json()
        except json.JSONDecodeError:

            if response.status_code == http.HTTPStatus.NO_CONTENT:
                data = list()
            else:
                LOGGER.error(response.text)
                raise

        return data

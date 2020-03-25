import logging
import urllib.parse
import requests
import json
import http

LOGGER = logging.getLogger(__name__)


class StorageSession(requests.Session):
    """
    Thing Things Network Data Storage API HTTP Session

    https://www.thethingsnetwork.org/docs/applications/storage/api.html
    """

    def __init__(self, base_url: str, access_key: str):
        super().__init__()

        self.base_url = base_url
        self.access_key = access_key

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

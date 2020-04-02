import http
import json
import logging
import urllib.parse

import requests

LOGGER = logging.getLogger(__name__)


class StorageSession(requests.Session):
    """
    Thing Things Network Data Storage API HTTP Session

    https://www.thethingsnetwork.org/docs/applications/storage/api.html

    To view the documentation, open session.docs_url in a web browser.
    """

    BASE_URL_FORMAT = 'https://{application_id}.data.thethingsnetwork.org/api/v2/'

    def __init__(self, application_id, access_key: str):
        super().__init__()

        self.application_id = application_id
        self.base_url = self.BASE_URL_FORMAT.format(application_id=self.application_id)
        self.access_key = access_key

        self.headers.update(self.extra_headers)

    @property
    def extra_headers(self):
        return {
            'Authorization': "key {access_key}".format(access_key=self.access_key),
        }

    @property
    def docs_url(self) -> str:
        """URL to Swagger API documentation"""
        return urllib.parse.urljoin(self.base_url, '/')

    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)

        for key, value in response.headers.items():
            LOGGER.debug("RESPONSE %s: %s", key, value)

        response.raise_for_status()
        return response

    def call_raw(self, endpoint: str, **kwargs) -> requests.Response:

        url = urllib.parse.urljoin(self.base_url, endpoint)

        return self.get(url, **kwargs)

    def call(self, *args, **kwargs) -> list:
        response = self.call_raw(*args, **kwargs)

        try:
            data = response.json()
        except json.JSONDecodeError:

            if response.status_code == http.HTTPStatus.NO_CONTENT:
                data = list()
            else:
                LOGGER.error(response.text)
                raise

        return data

    def query_raw(self, last: str = None):
        """
        https://mj-ttgopaxcounter.data.thethingsnetwork.org/#!/query/get_api_v2_query

        :param last: Duration on which we want to get the data (default 1h). Pass 30s for the last 30 seconds, 1h for
                     the last hour, 2d for the last 48 hours, etc
        :return: A collection of data points
        """
        return self.call_raw('query', params=dict(last=last))

    def query(self, *args, **kwargs) -> list:
        return self.query_raw(*args, **kwargs).json()

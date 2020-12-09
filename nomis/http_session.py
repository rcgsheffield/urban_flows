import logging
import urllib.parse
import json
import requests

LOGGER = logging.getLogger(__name__)


class NomisSession(requests.Session):
    BASE_URL = 'https://www.nomisweb.co.uk/api/v01/'

    @classmethod
    def build_url(cls, endpoint: str) -> str:
        return urllib.parse.urljoin(cls.BASE_URL, endpoint)

    def call(self, endpoint: str, **kwargs) -> dict:
        """
        Request API endpoint and process HTTP response
        """
        url = self.build_url(endpoint)

        # Log query parameters
        try:
            LOGGER.debug("PARAMS %s", kwargs['params'])
        except KeyError:
            pass

        # Make HTTP request
        response = self.get(url, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            LOGGER.error(response.text)
            raise

        # Parse JSON data
        try:
            data = response.json()
        except json.JSONDecodeError:
            LOGGER.error(response.text)
            raise

        # Check response data structure
        if set(data.keys()) != {'structure'}:
            LOGGER.error(data.keys())
            raise ValueError('Unexpected response contents', data.keys())

        # Log response headers
        for header, value in data['structure']['header'].items():
            LOGGER.debug("HEADER %s: %s", header, value)

        return data

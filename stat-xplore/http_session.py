import logging
import urllib.parse
import requests

LOGGER = logging.getLogger(__name__)


class StatSession(requests.Session):
    """
    Stat-Xplore : Open Data API

    https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API.html
    """

    BASE_URL = 'https://stat-xplore.dwp.gov.uk/webapi/rest/v1/'

    def __init__(self, api_key: str):
        super().__init__()
        self.headers.update({'APIKey': api_key})

    def build_url(self, endpoint: str) -> str:
        return urllib.parse.urljoin(self.BASE_URL, endpoint)

    def call(self, method: str = 'GET', endpoint: str = '', **kwargs):
        url = self.build_url(endpoint)
        response = self.request(method=method, url=url, **kwargs)

        # Raise HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            LOGGER.error(exc.response.text)
            raise

        # Log response headers
        for header, value in response.headers.items():
            LOGGER.debug("RESPONSE %s: %s", header, value)

        # TODO implement pagination
        if 'Link' in response.headers.keys():
            raise RuntimeError('Paginated response')

        # Parse JSON data
        return response.json()

    @property
    def info(self) -> dict:
        """
        General information about Stat-Xplore.

        https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API-Info.html
        """
        return self.call('info')

    @property
    def rate_limit(self):
        """
        https://stat-xplore.dwp.gov.uk/webapi/online-help/Open-Data-API-Rate-Limit.html
        """
        return self.call('rate_limit')

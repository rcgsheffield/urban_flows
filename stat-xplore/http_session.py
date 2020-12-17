import urllib.parse
import requests


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

    def call(self, endpoint: str, **kwargs):
        url = self.build_url(endpoint)
        response = self.get(url, **kwargs)
        response.raise_for_status()
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

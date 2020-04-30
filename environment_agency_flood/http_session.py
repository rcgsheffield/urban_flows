import logging
import urllib.parse
import requests

LOGGER = logging.getLogger(__name__)


class FloodSession(requests.Session):
    """
    Environment Agency real-time flood monitoring API HTTP session

    https://environment.data.gov.uk/flood-monitoring/doc/reference
    """

    BASE_URL = 'https://environment.data.gov.uk/flood-monitoring/id/'

    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)

        # HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            LOGGER.error(e)
            LOGGER.error(e.response.text)
            raise

        return response

    @classmethod
    def build_url(cls, endpoint: str) -> str:
        return urllib.parse.urljoin(cls.BASE_URL, endpoint)

    def _call(self, endpoint, **kwargs) -> requests.Response:
        """Base request"""

        url = self.build_url(endpoint)

        return self.get(url=url, **kwargs)

    def call(self, endpoint: str, **kwargs) -> dict:
        """Call JSON endpoint"""

        response = self._call(endpoint=endpoint, **kwargs)

        data = response.json()

        LOGGER.debug("Context: %s", data['@context'])
        for meta, value in data['meta'].items():
            LOGGER.debug("Meta: %s: %s", meta, value)

        return data

    def call_iter(self, endpoint: str, **kwargs) -> iter:
        """Generate lines of data"""

        response = self._call(endpoint=endpoint, stream=True, **kwargs)

        if response.encoding is None:
            response.encoding = 'utf-8'

        yield from response.iter_lines(decode_unicode=True)

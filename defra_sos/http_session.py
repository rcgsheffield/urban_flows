"""DEFRA SOS Session"""

import requests
import urllib.parse
import logging

LOGGER = logging.getLogger(__name__)

class DEFRASOSSession(requests.Session):
    """
    Defra’s UK-AIR Sensor Observation Service (SOS) API HTTP session

    https://uk-air.defra.gov.uk/data/about_sos
    """

    def _call(self, base_url, endpoint, **kwargs) -> requests.Response:
        """Base request"""

        # Build URL
        url = urllib.parse.urljoin(base_url, endpoint)

        response = self.get(url, **kwargs)

        # HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            LOGGER.error(e)
            LOGGER.error(e.response.text)
            raise

        return response

    def call(self, base_url: str, endpoint: str, **kwargs) -> dict:
        """Call JSON endpoint"""

        response = self._call(base_url, endpoint, **kwargs)

        data = response.json()

        return data

    def call_iter(self, base_url: str, endpoint: str, **kwargs) -> iter:
        """Generate lines of data"""

        response = self._call(base_url, endpoint, stream=True, **kwargs)

        yield from response.iter_lines(decode_unicode=True)


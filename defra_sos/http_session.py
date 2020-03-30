import requests
import urllib.parse
import logging

LOGGER = logging.getLogger(__name__)


class DEFRASOSSession(requests.Session):
    """
    DEFRA UK-AIR Sensor Observation Service (SOS) REST API HTTP session

    https://uk-air.defra.gov.uk/sos-ukair/static/doc/api-doc/
    """

    def __init__(self):
        super().__init__()

        self.headers.update({'User-Agent': 'Urban Flows Observatory'})

    def _call(self, base_url, endpoint, **kwargs) -> requests.Response:
        """Base request"""

        # Build URL
        url = urllib.parse.urljoin(base_url, endpoint)

        response = self.get(url, **kwargs)

        LOGGER.debug(response.text)

        # HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            LOGGER.error(e)
            LOGGER.error(e.response.text)
            raise

        return response

    def call(self, base_url: str, endpoint: str, **kwargs):
        """Call JSON endpoint"""

        response = self._call(base_url, endpoint, **kwargs)

        data = response.json()

        return data

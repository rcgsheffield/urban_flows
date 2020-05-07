import logging
import urllib.parse
import requests
import datetime

LOGGER = logging.getLogger(__name__)


class ZephyrSession(requests.Session):
    """
    EarthSense Zephyr API HTTP session
    """

    BASE_URL = "https://data.earthsense.co.uk/"
    # UTC time YYYYMMDDhhmm
    TIME_FORMAT = "%Y%m%d%H%M"

    def __init__(self, username: str, password: str):
        super().__init__()

        self.username = username
        self.password = password

    @classmethod
    def build_url(cls, endpoint: str) -> str:
        return urllib.parse.urljoin(cls.BASE_URL, endpoint)

    def _call(self, endpoint: str, **kwargs) -> requests.Response:
        """Call an endpoint and raise exceptions"""

        # Build URL
        url = self.build_url(endpoint)

        # Make HTTP request
        response = self.get(url, **kwargs)

        LOGGER.debug(response.content)

        # HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError:
            LOGGER.error(response.content)
            raise

        return response

    def call(self, *args, **kwargs):
        response = self._call(*args, **kwargs)
        data = response.json()

        # Raise API errors
        try:
            raise RuntimeError(data['error'])
        except KeyError:
            pass

        for key, value in data.items():
            LOGGER.debug("RESPONSE %s: %s", key, value)

        return data

    @property
    def version(self) -> dict:
        """API version"""
        return self.call('APIVersion')

    def iter_data(self, device_id: int, slot: str, start_time: datetime.datetime, end_time: datetime.datetime) -> iter:
        """Stream instrument data"""

        endpoint = 'dataForViewBySlotsAveraged/{username}/{password}/{device_id}/{start_time}/{end_time}/{slots}/{view}/{avg}/{format}/{target}'.format(
            username=self.username,
            password=self.password,
            device_id=device_id,
            start_time=start_time.strftime(self.TIME_FORMAT),
            end_time=end_time.strftime(self.TIME_FORMAT),
            slots=slot,
            view='def',
            # Unaveraged
            avg=0,
            format='csv',
            target='api',
        )

        response = self._call(endpoint, stream=True)

        # Count lines
        n = 0
        for line in response.iter_lines(decode_unicode=True):
            n += 1
            yield line

        LOGGER.info("Retrieved %s lines", n)

    @property
    def devices(self) -> dict:
        endpoint = "zephyrsForUser/{username}/{password}".format(username=self.username, password=self.password)

        data = self.call(endpoint)

        devices = data['usersZephyrs']

        return devices

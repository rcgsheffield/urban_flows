import logging
import urllib.parse
import requests

USER_AGENT = 'Urban Flows Observatory'

LOGGER = logging.getLogger(__name__)


class OizumSession(requests.Session):
    """
    Oizom API HTTP session

    https://production.oizom.com/documentation/
    """
    BASE_URL = 'https://production.oizom.com/v1/'

    def __init__(self, client_id, client_secret):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers.update({'User-Agent': USER_AGENT})
        self.authenticate()

    def request(self, *args, **kwargs):
        """Wrapper for all HTTP requests"""
        response = super().request(*args, **kwargs)

        # Log request headers
        for header, value in response.request.headers.items():
            LOGGER.debug("REQUEST %s: %s", header, value)

        # Raise HTTP errors as exceptions
        try:
            response.raise_for_status()
        except requests.HTTPError as http_error:
            LOGGER.error(http_error)
            LOGGER.error(http_error.response.json())
            raise

        # Log response headers
        for header, value in response.headers.items():
            LOGGER.debug("RESPONSE %s: %s", header, value)

        return response

    def call(self, endpoint: str, post: bool = False, **kwargs):
        """Call and API endpoint"""
        url = urllib.parse.urljoin(self.BASE_URL, endpoint)
        response = self.request(url=url, method='post' if post else 'get', **kwargs)
        return response.json()

    @property
    def access_token(self) -> str:
        payload = dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type='client_credentials',
            scope='view_data',
        )
        data = self.call('oauth2/token', json=payload, post=True)
        return data['access_token']

    def authenticate(self):
        """Generate an login token"""

        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'ClientId': self.client_id,
        }
        self.headers.update(headers)

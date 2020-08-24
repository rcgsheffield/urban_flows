import logging
import urllib.parse
import pathlib
import configparser

import requests

LOGGER = logging.getLogger(__name__)


class AeroqualSession(requests.Session):
    BASE_URL = 'https://cloud.aeroqual.com/api/'

    def __init__(self, config_file: pathlib.Path):
        super().__init__()
        self.config_file = pathlib.Path(config_file)
        self._config = None

        self.login()

    @classmethod
    def build_url(cls, endpoint: str) -> str:
        return urllib.parse.urljoin(cls.BASE_URL, endpoint)

    @property
    def config(self) -> configparser.ConfigParser:
        """Load configuration options"""
        if not self._config:
            with self.config_file.open() as file:
                config = configparser.RawConfigParser()
                config.read_file(file)
                self._config = config
        return self._config

    @property
    def credentials(self) -> dict:
        return dict(
            username=self.config['credentials']['username'],
            password=self.config['credentials']['password'],
        )

    @property
    def username(self) -> str:
        return self.credentials['username']

    @property
    def password(self) -> str:
        return self.credentials['password']

    def login(self):
        """
        Log in to API – must be performed before sending any other API request. On success, use the contents of the
        “Set-Cookie” header as the “Cookie” header for all subsequent API requests.
        """
        endpoint = 'account/login'
        url = self.build_url(endpoint)
        return self.post(url, data=dict(UserName=self.username, Password=self.password))

    def request(self, *args, **kwargs):
        # Wrap request, but raise errors
        response = super().request(*args, **kwargs)

        for header, value in response.request.headers.items():
            LOGGER.debug("REQUEST %s: %s", header, value)
        for header, value in response.headers.items():
            LOGGER.debug("RESPONSE %s: %s", header, value)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            LOGGER.error(e)
            LOGGER.error(e.response.text)
            raise
        return response

    def call(self, endpoint: str, **kwargs) -> dict:
        url = self.build_url(endpoint=endpoint)
        response = self.get(url, **kwargs)
        try:
            data = response.json()
            LOGGER.debug(data)
            return data
        except:
            LOGGER.error(response.text)
            raise

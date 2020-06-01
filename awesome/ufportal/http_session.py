import logging
import pathlib
import json

import requests

LOGGER = logging.getLogger(__name__)


class PortalSession(requests.Session):
    TOKEN_PATH = pathlib.Path.home().joinpath('awesome_token.txt')
    LANGUAGE = 'en'

    def __init__(self):
        super().__init__()
        self.headers.update(self.extra_headers)

    @property
    def extra_headers(self):
        return {
            'Authorization': 'Bearer ' + self.token,
            'Accept-Language': self.LANGUAGE,
        }

    @property
    def token_path(self):
        return pathlib.Path(self.TOKEN_PATH)

    def request(self, *args, **kwargs) -> dict:
        response = super().request(*args, **kwargs)

        # Log payload
        for key in ('data', 'json', 'params'):
            try:
                LOGGER.debug("%s %s", key.upper(), kwargs[key])
            except KeyError:
                pass

        # Log HTTP headers
        for header, value in response.headers.items():
            LOGGER.debug("RESPONSE %s: %s", header, value)

        # Raise errors
        try:
            response.raise_for_status()
        except requests.HTTPError:
            LOGGER.error(response.text)
            raise

        # Parse JSON payload
        return response.json()

    @property
    def token(self) -> str:
        with self.token_path.open() as file:
            return file.read().strip()

    def get_iter(self, url, **kwargs):
        """Paginated API call"""
        # Iterate over pages
        while True:
            try:
                body = self.get(url, **kwargs)

            # End pagination
            except requests.exceptions.MissingSchema:
                if url:
                    raise
                else:
                    break

            for key, value in body['meta'].items():
                LOGGER.debug("META %s: %s", key, value)

            yield from body['data']

            url = body['links']['next']

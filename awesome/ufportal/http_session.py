"""
HTTP transport layer
"""

import logging
import pathlib
import json

import requests

LOGGER = logging.getLogger(__name__)


class PortalSession(requests.Session):
    LANGUAGE = 'en'

    def __init__(self, token_path: pathlib.Path):
        super().__init__()
        self.token_path = pathlib.Path(token_path)
        self.headers.update(self.extra_headers)

    @property
    def extra_headers(self):
        return {
            'Authorization': 'Bearer ' + self.token,
            'Accept-Language': self.LANGUAGE,
        }

    def request(self, *args, **kwargs) -> dict:
        """Make a HTTP request to the API and parse the response"""

        headers = {
            'Accept': 'application/json',
        }
        headers.update(kwargs.pop('headers', dict()))

        # Debug log request payload
        for key in ('data', 'json', 'params'):
            try:
                LOGGER.debug("REQUEST %s: %s", key, kwargs[key])
            except KeyError:
                pass

        # Make the request
        response = super().request(*args, headers=headers, **kwargs)

        for r in response.history:
            # Log headers
            for header, value in r.request.headers.items():
                LOGGER.debug("REQUEST %s: %s", header, value)
            for header, value in r.headers.items():
                LOGGER.debug("RESPONSE %s: %s", header, value)

        # Raise errors
        try:
            response.raise_for_status()

        # Log HTTP error codes
        except requests.HTTPError:
            LOGGER.error(response.text)
            raise

        # Parse JSON response
        try:
            return response.json()

        # Log invalid JSON responses
        except json.JSONDecodeError as e:
            LOGGER.error(e)
            LOGGER.error(response.text)
            raise

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

"""
HTTP transport layer for the Awesome portal
"""

import logging
import json

import requests

LOGGER = logging.getLogger(__name__)


class PortalSession(requests.Session):
    LANGUAGE = 'en'

    def __init__(self, token: str):
        super().__init__()

        self.token = token
        self.headers.update(self.extra_headers)

    @property
    def extra_headers(self):
        return {
            'Authorization': 'Bearer ' + self.token,
            'Accept-Language': self.LANGUAGE,
        }

    def request(self, *args, **kwargs):
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

        for _response in response.history:
            # Log headers
            for header, value in _response.request.headers.items():
                LOGGER.debug("REQUEST %s: %s", header, value)
            for header, value in _response.headers.items():
                LOGGER.debug("RESPONSE %s: %s", header, value)

        # Raise errors
        try:
            response.raise_for_status()

        # Log HTTP error codes
        except requests.HTTPError as exc:
            LOGGER.error(response.headers)
            LOGGER.error(response.text)
            raise

        return response

    def call(self, *args, method: str = 'get', **kwargs) -> dict:
        response = self.request(method, *args, **kwargs)

        # Parse JSON response
        try:
            return response.json()

        # Log invalid JSON responses
        except json.JSONDecodeError as e:
            LOGGER.error(e)
            LOGGER.error(response.text)
            raise

    def get_iter(self, url, **kwargs):
        """Paginated API call"""
        # Iterate over pages
        while True:
            try:
                body = self.call(url, **kwargs)

            # End pagination
            except requests.exceptions.MissingSchema:
                if url:
                    raise
                else:
                    break

            yield from body['data']

            # Go to next page
            url = body['links']['next']

"""
HTTP transport layer for the Awesome portal
"""

import logging
import json
import time

import requests

LOGGER = logging.getLogger(__name__)


class PortalSession(requests.Session):
    LANGUAGE = 'en'

    def __init__(self, token: str):
        super().__init__()
        self.headers.update({
            'Authorization': 'Bearer ' + token,
            'Accept-Language': self.LANGUAGE,
        })

    def request(self, *args, **kwargs):
        """Make a HTTP request to the API and parse the response"""

        headers = {'Accept': 'application/json'}
        headers.update(kwargs.pop('headers', dict()))

        # Make the request
        response = super().request(*args, headers=headers, **kwargs)

        for i, _response in enumerate(response.history):
            # Log headers
            for header, value in _response.request.headers.items():
                LOGGER.debug("REQUEST %s %s: %s", i, header, value)
            for header, value in _response.headers.items():
                LOGGER.debug("RESPONSE %s %s: %s", i, header, value)

        # Raise errors
        try:
            response.raise_for_status()

        # Log HTTP error codes
        except requests.HTTPError as exc:
            for header, value in exc.response.headers.items():
                LOGGER.info("RESPONSE HEADER %s: %s", header, value)
            LOGGER.error(exc.response.text)
            raise

        return response

    def call(self, *args, method: str = 'get', **kwargs) -> dict:
        response = self.request(method, *args, **kwargs)
        LOGGER.debug("HTTP request took %s seconds",
                     response.elapsed.total_seconds())

        # Prevent redirect
        if response.history:
            for r in response.history:
                LOGGER.error(r)
                LOGGER.error(r.url)
            raise ValueError(response.history)

        # Parse JSON response
        try:
            return response.json()

        # Log invalid JSON responses
        except json.JSONDecodeError as exc:
            LOGGER.error(exc)
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

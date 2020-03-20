import logging
import datetime
import requests

import requests_cache

LOGGER = logging.getLogger(__name__)

CACHE_EXPIRE_AFTER = datetime.timedelta(days=1)


class DEFRASession(requests_cache.CachedSession):
    """DEFRA HTTP session"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, expire_after=CACHE_EXPIRE_AFTER)

        # Python code is blocked so replace user agent string
        self.headers.update({'User-Agent': 'Urban Flows Observatory'})

    def request(self, *args, **kwargs) -> requests.Response:
        """Wrapper to raise exceptions for HTTP errors"""

        response = super().request(*args, **kwargs)

        self.log_headers(response)

        response.raise_for_status()

        return response

    @classmethod
    def log_headers(cls, response):
        """Log header info"""

        for headers, prefix in ((response.request.headers, 'REQUEST'), (response.headers, 'RESPONSE')):
            for header, value in headers.items():
                LOGGER.debug("%s %s: %s", prefix, header, value)

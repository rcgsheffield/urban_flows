import logging
import requests
from typing import Iterable

LOGGER = logging.getLogger(__name__)


class FingertipsSession(requests.Session):
    def _call(self, *args, **kwargs) -> requests.Response:
        response = self.get(*args, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            LOGGER.error(exc)
            LOGGER.error(exc.response.content)
            raise
        return response

    def call(self, *args, **kwargs) -> dict:
        return self._call(*args, **kwargs).json()

    def call_iter(self, *args, **kwargs) -> Iterable[str]:
        # https://requests.readthedocs.io/en/master/user/advanced/#streaming-requests
        response = self._call(*args, stream=True, **kwargs)

        if response.encoding is None:
            response.encoding = 'utf-8'

        yield from response.iter_lines(decode_unicode=True)

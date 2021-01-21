import logging
import requests

LOGGER = logging.getLogger(__name__)


class FingertipsSession(requests.Session):
    def call(self, *args, **kwargs) -> dict:
        response = self.get(*args, **kwargs)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            LOGGER.error(exc)
            LOGGER.error(exc.response.content)
            raise
        return response.json()

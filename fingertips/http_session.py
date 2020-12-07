import requests


class FingertipsSession(requests.Session):
    def call(self, *args, **kwargs) -> dict:
        response = self.get(*args, **kwargs)
        response.raise_for_status()
        return response.json()

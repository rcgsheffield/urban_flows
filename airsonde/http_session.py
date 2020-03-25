import urllib.parse
import requests


class OizumSession(requests.Session):
    """
    Oizom API HTTP session

    https://production.oizom.com/documentation/
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    def call(self, endpoint: str):
        url = urllib.parse.urljoin(self.base_url, endpoint)
        payload = dict(
            client_id=CLIENT_ID,
            client_secret=getpass.getpass('Enter client secret: '),
            grant_type='client_credentials',
            scope='view_data',
        )
        response = session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        jprint(data)

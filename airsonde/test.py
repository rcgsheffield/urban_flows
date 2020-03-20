import logging
import urllib.parse
import requests
import json

import getpass

BASE_URL = 'https://production.oizom.com/v1/'
CLIENT_ID = '9252ac5b-211d-4071-8797-9a9bd0993ace'


def jprint(obj, indent=2, **kwargs):
    print(json.dumps(obj, indent=indent, **kwargs))


def main():
    logging.basicConfig(level=logging.DEBUG)
    session = requests.Session()

    url = urllib.parse.urljoin(BASE_URL, 'oauth2/token')
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

    token = data['access_token']
    headers = {
        'Authorization': f'Bearer {token}',
        'ClientId': CLIENT_ID,
    }
    session.headers.update(headers)

    url = urllib.parse.urljoin(BASE_URL, 'devices')
    response = session.get(url)
    response.raise_for_status()
    data = response.json()
    jprint(data)


if __name__ == '__main__':
    main()

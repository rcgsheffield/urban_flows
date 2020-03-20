"""
This is a script to test the web server (akin to using CURL).
"""
import logging
import requests
import argparse
import getpass

LOGGER = logging.getLogger(__name__)

DEFAULT_URL = 'https://ufdlsrv01.shef.ac.uk/ott/'

DEFAULT_STATION_ID = '0123456789'

ACTIONS = {
    'senddata': 'senddata.xml',
    'sendalarm': 'sendalarm.xml'
}

HEADERS = {
    'Content-Type': 'application/xml'
}


def load_data(path: str):
    """Load test data to send"""

    with open(path) as file:
        LOGGER.info("Loaded '%s'", file.name)
        return file.read()


def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)

    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', default=DEFAULT_URL, help="Target server base URL")
    parser.add_argument('-a', '--action', default='senddata', help="Logger action type")
    parser.add_argument('-n', '--username', help="Basic authentication credential")
    parser.add_argument('-v', '--noverify', action='store_true', help="Do not verify SSL certificates")
    parser.add_argument('-s', '--stationid', default=DEFAULT_STATION_ID, help="Do not verify SSL certificates")
    args = parser.parse_args()

    # Basic authentication
    auth = None
    if args.username:
        auth = (args.username, getpass.getpass('Enter password: '))

    # Initialise web session
    session = requests.Session()
    session.auth = auth
    session.verify = not args.noverify

    # Load data for this action
    data_path = ACTIONS[args.action]
    data = load_data(data_path)

    # Build target URL

    # Build request payload
    params = dict(
        stationid=args.stationid,
        action=args.action,
    )

    # Send HTTP data
    response = session.post(url=args.url, params=params, data=data, headers=HEADERS)
    response.raise_for_status()

    # Log headers
    for header, value in response.headers.items():
        LOGGER.debug("%s: %s", header, value)

    print(response.text)


if __name__ == '__main__':
    main()

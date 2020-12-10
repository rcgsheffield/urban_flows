import logging
import urllib.parse
import requests
from typing import Union

LOGGER = logging.getLogger(__name__)


class CKANSession(requests.Session):
    """
    https://guidance.data.gov.uk/get_data/api_documentation/#api-documentation
    """
    BASE_URL = 'https://data.gov.uk/api/action/'

    def call(self, endpoint: str, **kwargs) -> Union[list, dict]:
        """
        Make an API request
        https://docs.ckan.org/en/2.7/api/index.html#making-an-api-request

        To call the CKAN API, post a JSON dictionary in an HTTP POST request to one of CKAN’s API URLs. The parameters
        for the API function should be given in the JSON dictionary. CKAN will also return its response in a JSON
        dictionary.
        """
        url = urllib.parse.urljoin(self.BASE_URL, endpoint)
        response = self.post(url=url, **kwargs)
        response.raise_for_status()
        data = response.json()

        # Process API response

        # the documentation string for the function you called.
        LOGGER.info("HELP %s", data['help'])

        # Check for application errors
        if not data['success']:
            for key, value in data['error'].items():
                LOGGER.error("%s: %s", key, value)
            raise RuntimeError(data['error'])

        return data['result']

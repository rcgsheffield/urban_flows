import logging
import urllib.parse
import requests
import json

BASE_URL = 'https://www.nomisweb.co.uk/api/v01/'
LOGGER = logging.getLogger(__name__)

SESSION = requests.Session()


def build_url(endpoint: str) -> str:
    return urllib.parse.urljoin(BASE_URL, endpoint)


def call(endpoint: str, **kwargs) -> dict:
    """
    Request API endpoint and process HTTP response
    """
    url = build_url(endpoint)

    # Log query parameters
    try:
        LOGGER.debug("PARAMS %s", kwargs['params'])
    except KeyError:
        pass

    response = SESSION.get(url, **kwargs)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        LOGGER.error(response.text)
        raise

    try:
        data = response.json()
    except json.JSONDecodeError:
        LOGGER.error(response.text)
        raise

    # Check response data structure
    if set(data.keys()) != {'structure'}:
        LOGGER.error(data.keys())
        raise ValueError('Unexpected response contents', data.keys())

    for header, value in data['structure']['header'].items():
        LOGGER.debug("HEADER %s: %s", header, value)

    return data


def main():
    logging.basicConfig(level=logging.DEBUG)

    # Discover data
    # url = build_url('dataset/def.sdmx.json?search=*business*')
    # url = build_url('dataset/NM_200_1/def.sdmx.json')
    # url = build_url('dataset/NM_1_1/geography.def.sdmx.json')
    # url = build_url('dataset/NM_1_1/geography/2092957699.def.sdmx.json')
    # 2092957699TYPE449 nuts 2013 level 3 within England
    # url = build_url('dataset/NM_1_1/geography/2092957699TYPE449.def.sdmx.json')
    # 1883242530 Sheffield
    # url = build_url('dataset/NM_1_1/geography/1883242530.def.sdmx.json')
    # 2092957699TYPE61 postcode towns within England
    # url = build_url('dataset/NM_1_1/geography/2092957699TYPE61.def.sdmx.json')
    # 2092957699TYPE61 => 255852611 Sheffield
    # url = build_url('dataset/NM_1_1/geography/255852611.def.sdmx.json')
    # 255852611TYPE62 postcode districts within Sheffield
    # url = build_url('dataset/NM_1_1/geography/255852611TYPE62.def.sdmx.json')
    # 255852611TYPE63 postcode sectors within Sheffield
    # url = build_url('dataset/NM_1_1/geography/255852611TYPE63.def.sdmx.json')
    # /api/v01/dataset/NM_1_1/jsonstat.json?geography=2038432081&sex=5&item=1&measures=20100&time=latest
    # url = build_url('dataset/NM_1_1/jsonstat.json')
    # NM_189_1 Business Register and Employment Survey
    # url = build_url('dataset/NM_189_1/jsonstat.json')
    # url = build_url('dataset/NM_189_1/def.sdmx.json')
    # params = dict(time='latest', geography='default')

    # NM_189_1 Business Register and Employment Survey
    key_family_uri = 'NM_189_1'
    endpoint = 'dataset/{}/def.sdmx.json'.format(key_family_uri)
    data = call(endpoint)

    # Code lists
    try:
        for code_list in data['structure']['codelists']['codelist']:
            print('Agency:', code_list['agencyid'])
            for code in code_list['code']:
                print(code['value'], code['description']['value'])
    except KeyError:
        pass

    # Key families
    params = dict()
    for key_family in data['structure']['keyfamilies']['keyfamily']:
        # key_family: dict_keys(['agencyid', 'annotations', 'id', 'components', 'name', 'uri', 'version'])
        LOGGER.debug(key_family.keys())
        print(key_family['uri'], key_family['id'], key_family['name']['value'])

        for annotation in key_family['annotations']['annotation']:
            print(annotation)

        for dimension in key_family['components']['dimension']:
            print(dimension)
            params[dimension['conceptref'].casefold()] = 'default'

    endpoint_data = urllib.parse.urljoin(endpoint, '{}.jsonstat.json'.format(key_family_uri))
    call(endpoint_data, params=params)


if __name__ == '__main__':
    main()

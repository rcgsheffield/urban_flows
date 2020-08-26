"""
Retrieve data from the Urban Flows Observatory data warehouse via the Urban Flows Data Extraction tool

Usage:
    query = dict(
        time_period=[
            datetime.datetime(2020, 3, 2),
            datetime.datetime(2020, 3, 3),
        ],
        metrics={
            'AQ_NO',
            'AQ_CO',
        },
        site_ids={
            'S0009',
            'S0008',
        }
    )

    for row in run(query):
        ...
"""

import logging
import requests
import datetime

from collections import OrderedDict

URL = 'https://sheffield-portal.urbanflows.ac.uk/uflobin/ufdex'

LOGGER = logging.getLogger(__name__)

NULL = -32768


def stream(time_period, site_ids: iter = None) -> iter:
    """Retrieve raw data over HTTP"""

    # Query database
    params = dict(
        Tfrom=time_period[0].isoformat(),
        Tto=time_period[1].isoformat(),
        aktion='CSV_show',
        freqInMin=5,
        tok='generic',
    )

    if site_ids:
        params['bySite'] = ','.join(site_ids),

    with requests.Session() as session:
        # Streaming Requests
        # https://requests.readthedocs.io/en/master/user/advanced/#streaming-requests
        response = session.get(URL, stream=True, params=params)

    # Raise HTTP errors
    try:
        response.raise_for_status()
    except requests.HTTPError:
        LOGGER.error(response.text)
        raise

    # Provide a fallback encoding in the event the server doesn’t provide one
    if not response.encoding:
        response.encoding = 'utf-8'

    # Generate lines of data
    return response.iter_lines(decode_unicode=True)


def parse(query: dict) -> iter:
    """Process raw data and generate rows of useful data"""

    for line in stream(**query):

        if line.startswith('#'):
            LOGGER.debug(line)

            if line.startswith('# Begin CSV table'):
                # Reset variables
                site_id = None
                headers = list()
                number_of_points = None
                n_rows = 0

            elif line.startswith('# number of points:'):
                number_of_points = int(line.partition(': ')[2])

            # Get column meta-data
            elif line.startswith('# Column_'):
                # Parse arbitrary comment
                label = line[2:].split(' / ')[1]
                headers.append(label)

            elif line.startswith('# site.id'):
                site_id = line.split()[-1]

            elif line.startswith('# End CSV table'):

                # Check row count
                if n_rows != number_of_points:
                    raise ValueError('Unexpected row count, expected %s but got %s' % number_of_points, n_rows)

        elif line:

            # Skip HTML
            if line.startswith('<pre>'):
                continue

            # Build dictionary
            values = line.split(',')

            # Check column count
            if len(values) != len(headers):
                raise ValueError('Unexpected number of data values')

            row = OrderedDict(zip(headers, values))

            row['site_id'] = site_id

            yield row

            n_rows += 1


def remove_nulls(row: dict) -> dict:
    """Re-build dictionary without missing values"""
    return {k: None if v == NULL else v for k, v in row.items()}


def parse_timestamp(timestamp: int) -> str:
    """Parse UTX unix timestamp"""
    return datetime.datetime.utcfromtimestamp(timestamp).isoformat()


def remove_prefix(row: dict, sep: str = '~') -> dict:
    """Remove label prefix e.g. 'data~time' becomes 'time'"""
    return {key.rpartition(sep)[2]: value for key, value in row.items()}


def transform(row: dict) -> dict:
    row = remove_nulls(row)
    row['data~time'] = parse_timestamp(float(row['data~time']))
    row = remove_prefix(row)

    return row


def run(query: dict) -> iter:
    for row in parse(query):
        yield transform(row)

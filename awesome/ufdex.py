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

from typing import Iterable, Dict, Sequence
from collections import OrderedDict

import settings

# URL = 'https://sheffield-portal.urbanflows.ac.uk/uflobin/ufdex'
URL = 'http://ufdev.shef.ac.uk/uflobin/ufdexF0'

LOGGER = logging.getLogger(__name__)

NULL = -32768.0


class UrbanFlowsQuery:
    """
    Retrieve data from the Urban Flows Observatory data extraction tool by specifying filters.
    """

    # 2020-01-23T10:20:32
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    TIME_COLUMN = 'TIME_UTC_UNIX'

    def __init__(self, time_period: Sequence[datetime.datetime], site_ids: set = None,
                 sensors: set = None):
        """
        :param time_period: tuple[datetime, datetime]
        :param site_ids: Filter locations
        """
        self.time_period = time_period
        self.site_ids = set(site_ids or set())
        self.sensors = set(sensors or set())

    @property
    def time_period(self):
        return self._time_period

    @time_period.setter
    def time_period(self, time_period: tuple):

        for t in time_period:
            if not t:
                raise ValueError('Time period undefined')

        if time_period[1] < time_period[0]:
            raise ValueError('End time before start time')

        self._time_period = tuple((t.replace(microsecond=0) for t in time_period))

    @property
    def time_from(self) -> str:
        return self.format_timestamp(self.time_period[0])

    @property
    def time_to(self) -> str:
        return self.format_timestamp(self.time_period[1])

    @classmethod
    def format_timestamp(cls, t: datetime.datetime) -> str:
        return t.replace(microsecond=0).strftime(cls.TIME_FORMAT)

    def generate_time_periods(self, freq: datetime.timedelta) -> Iterable[tuple]:
        start, end = self.time_period
        t0, t1 = start, start + freq

        while True:

            if t1 > end:
                yield t0, end
                break
            else:
                yield t0, t1

            t0 += freq
            t1 += freq

    def stream(self) -> Iterable[str]:
        """Retrieve raw data over HTTP"""
        with requests.Session() as session:
            for start, end in self.generate_time_periods(freq=settings.URBAN_FlOWS_TIME_CHUNK):

                # Prepare query parameters
                params = dict(
                    Tfrom=self.format_timestamp(start),
                    Tto=self.format_timestamp(end),
                    aktion='CSV_show',
                    freqInMin=5,
                    tok='generic',
                )

                if self.sensors:
                    params['bySensor'] = ','.join(self.sensors)

                if self.site_ids:
                    params['bySite'] = ','.join(self.site_ids)

                # Streaming Requests
                # https://requests.readthedocs.io/en/master/user/advanced/#streaming-requests
                response = session.get(URL, stream=True, params=params)

                # Raise HTTP errors
                try:
                    response.raise_for_status()
                except requests.HTTPError:
                    LOGGER.error(response.text)
                    raise

                # Provide a fallback encoding in the event the server doesn't provide one
                if not response.encoding:
                    response.encoding = 'utf-8'

                # Generate lines of data
                yield from response.iter_lines(decode_unicode=True)

    @staticmethod
    def parse(lines: Iterable[str]) -> Iterable[Dict]:
        """
        Process raw data and generate rows of useful data
        """

        for line in lines:
            LOGGER.debug(line)

            # Metadata comments
            if line.startswith('#'):

                # New data set for each sensor
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
                    # Parse comment
                    # ColDescription: name / units / UCD / description / type / no-data-value
                    # e.g. "Column_6 / data~airtemp / C / MET_TEMP / Air temperature / float / -32768"
                    label = line[2:].split(' / ')[3]  # get the "UCD" value
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

                if not site_id:
                    raise ValueError('No site_id value')
                row['site_id'] = site_id

                yield row

                n_rows += 1

    @staticmethod
    def remove_nulls(row: dict) -> dict:
        """Re-build dictionary without missing values"""
        return {k: v for k, v in row.items() if v != NULL}

    @staticmethod
    def parse_timestamp(timestamp: float) -> datetime.datetime:
        """Parse UTX unix timestamp"""
        return datetime.datetime.utcfromtimestamp(timestamp)

    @staticmethod
    def parse_data_types(row: dict) -> dict:
        """
        Parse data types: values are floats
        """
        # Don't parse these columns
        non_floats = {'site_id', 'ID_MAIN', 'TIME_UTC_UNIX'}
        try:
            row = {key: value if key in non_floats else float(value) for key, value in row.items()}
        except (TypeError, ValueError):
            LOGGER.error(row)
            raise
        return row

    @classmethod
    def transform(cls, row: dict) -> dict:
        row[cls.TIME_COLUMN] = cls.parse_timestamp(float(row[cls.TIME_COLUMN]))
        row = cls.parse_data_types(row)
        row = cls.remove_nulls(row)

        return row

    def __call__(self, *args, **kwargs):
        row_count = 0
        for row in self.parse(self.stream()):
            yield self.transform(row)
            row_count += 1

        LOGGER.info("Generated %s rows", row_count)

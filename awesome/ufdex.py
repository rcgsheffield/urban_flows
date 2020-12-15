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

    for reading in run(query):
        ...
"""

import datetime
import itertools
import logging
from typing import Iterable, Dict, Sequence

import requests

import settings

URL = 'http://ufdev.shef.ac.uk/uflobin/ufdexF1'

LOGGER = logging.getLogger(__name__)

NULL = -32768.0


class UrbanFlowsQuery:
    """
    Retrieve data from the Urban Flows Observatory data extraction tool by specifying filters.
    """

    # 2020-01-23T10:20:32
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
    TIME_COLUMN = 'TIME_UTC_UNIX'
    DATA_TYPES = {
        'float': float,
        'int': int,
    }

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
        Process raw data and generate one dictionary per reading
        """
        # One item for each column
        columns = list()
        meta = dict()
        n_rows = 0

        for line in lines:

            # Query fail
            if line == 'mutis csvShow 0 sensors satisfy your conditions':
                return

            # Metadata comments
            if line.startswith('#'):

                # New data set for each sensor
                if line.startswith('# Begin CSV table'):
                    # Reset variables
                    meta = dict()
                    columns = list()
                    number_of_points = None
                    n_rows = 0

                elif line.startswith('# number of points:'):
                    number_of_points = int(line.partition(': ')[2])

                # ColDescription: name / units / UCD / description / type / no-data-value
                elif line.startswith('# ColDescription'):
                    _, _, desc_str = line.partition(':')
                    col_desc = tuple((s.strip() for s in desc_str.split('/')))

                # Get column meta-data
                elif line.startswith('# Column_'):
                    # Column_1 / data.time / s / TIME_UTC_UNIX / Time in seconds since 1970.0, or UNIX time / utime / -32768
                    # Column_2 / data.sensor /  / ID_MAIN / Sensor ID (numerical values) / int / -32768
                    # Column_3 / data.CO / ppm / AQ_CO / Carbon Monoxide / float / -32768

                    # Skip "Column_n"
                    col_labels = (s.strip() for s in line[2:].split('/')[1:])

                    columns.append(dict(itertools.zip_longest(col_desc, col_labels)))

                elif line.startswith('# End CSV table'):

                    # Check row count
                    if n_rows != number_of_points:
                        raise ValueError('Unexpected row count, expected %s but got %s' % number_of_points, n_rows)

                # Other metadata
                elif line.startswith('# sensor') or line.startswith('# site'):
                    key, _, value = line[2:].partition(': ')
                    meta[key] = value

            elif line:
                time = None

                # Skip HTML
                if line.startswith('<'):
                    continue

                # Build dictionary
                values = line.split(',')

                # Check column count
                if len(values) != len(columns):
                    for col in columns:
                        LOGGER.error(col)
                    LOGGER.error(values)
                    raise ValueError('Unexpected number of data values')

                for i, value in enumerate(values):
                    reading = columns[i].copy()
                    reading.update(meta)
                    reading['value'] = value

                    if reading['name'] == 'data.time':
                        time = reading['value']
                    elif reading['name'] == 'data.sensor':
                        pass
                    else:
                        assert time
                        reading['time'] = time
                        yield reading

                n_rows += 1

        LOGGER.info("Retrieved %s rows", n_rows)

    @classmethod
    def parse_data_types(cls, reading: dict) -> dict:
        """
        Parse data types: values are floats
        """

        data_type = cls.DATA_TYPES.get(reading['type'], str)

        try:
            reading['value'] = data_type(reading['value'])
            reading['no-data-value'] = data_type(reading['no-data-value'])
            reading['time'] = datetime.datetime.utcfromtimestamp(int(reading['time']))
        except (TypeError, ValueError):
            LOGGER.error(data_type)
            LOGGER.error(reading)
            raise

        return reading

    @classmethod
    def transform(cls, reading: dict) -> dict:
        reading = cls.parse_data_types(reading)

        return reading

    def __call__(self, *args, **kwargs):
        reading_count = 0
        null_count = 0
        for reading in self.parse(self.stream()):
            reading = self.transform(reading)

            # Filter nulls
            if reading['value'] == float():
                null_count += 1
                continue

            yield reading

            reading_count += 1

        LOGGER.info("Generated %s readings (removed %s nulls)", reading_count, null_count)

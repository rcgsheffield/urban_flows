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
from typing import Iterable, Dict, List, Sequence, Set, Tuple

import requests

import settings
from settings import HOST, URL

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

    def __init__(self, time_period: Sequence[datetime.datetime],
                 site_ids: Set[str] = None, sensors: Set[str] = None,
                 families: Set[str] = None, freq: datetime.timedelta = None):
        """
        :param time_period: tuple[datetime, datetime]
        :param site_ids: Filter locations
        :param sensors: UFO sensor ids
        :param families: UFO sensor family names
        :param freq: Query chunk size
        """
        self.time_period = time_period
        self.site_ids = set(site_ids or set())
        self.sensors = set(sensors or set())
        self.families = set(families or set())
        self.freq = freq or settings.URBAN_FlOWS_TIME_CHUNK

    def __call__(self, *args, **kwargs):
        reading_count = 0
        null_count = 0
        for reading in self.parse(self.stream()):
            reading = self.transform(reading)

            # Filter nulls
            if reading['value'] is None:
                null_count += 1
                continue

            yield reading

            reading_count += 1

        LOGGER.info("Generated %s readings (after removing %s nulls)",
                    reading_count, null_count)

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

        self._time_period = tuple(
            (t.replace(microsecond=0) for t in time_period))

    @property
    def time_from(self) -> str:
        return self.format_timestamp(self.time_period[0])

    @property
    def time_to(self) -> str:
        return self.format_timestamp(self.time_period[1])

    @classmethod
    def format_timestamp(cls, t: datetime.datetime) -> str:
        return t.replace(microsecond=0).strftime(cls.TIME_FORMAT)

    @staticmethod
    def generate_time_periods(start: datetime.datetime,
                              end: datetime.datetime,
                              freq: datetime.timedelta) -> \
            Iterable[Tuple[datetime.datetime]]:
        """
        Break the time period into chunks of size `freq`
        """

        t0, t1 = start, start + freq

        while True:

            if t1 >= end:
                yield t0, end
                break
            else:
                yield t0, t1

            t0 += freq
            t1 += freq

    def stream(self, **kwargs) -> Iterable[str]:
        """
        Retrieve raw data over HTTP
        """

        # Prepare query parameters
        params = dict(
            Tfrom=self.format_timestamp(self.time_period[0]),
            Tto=self.format_timestamp(self.time_period[1]),
            aktion='CSV_show',
            freqInMin=5,
            tok='generic',
        )

        # Build filters via HTTP query parameters
        # e.g. "byFamily=AMfixed,luftdaten"
        filters = {
            'bySensor': self.sensors,
            'bySite': self.site_ids,
            'byFamily': self.families,
        }
        for query, values in filters.items():
            if values:
                params[query] = ','.join(values)

        LOGGER.info("QUERY %s", params)
        yield from self._stream(params=params, **kwargs)

    @staticmethod
    def _stream(**kwargs) -> Iterable[str]:
        with requests.Session() as session:
            # Streaming Requests
            with session.get(URL, stream=True, **kwargs) as response:

                # Raise HTTP errors
                try:
                    response.raise_for_status()
                except requests.HTTPError:
                    LOGGER.error(response.text)
                    raise

                # Provide a fallback encoding in the event the server doesn't
                # provide one
                if not response.encoding:
                    response.encoding = 'utf-8'

                # Generate lines of data
                yield from response.iter_lines(decode_unicode=True)

    @staticmethod
    def readlines(data: Iterable[bytes], sep: str = '\n',
                  encoding: str = 'utf-8') -> Iterable[str]:
        """
        Read a stream of bytes and yield one string per line
        """

        line = str()

        # Iterate over chunks of binary data
        for chunk in data:
            # Decode chunk of data into a string, which may contain
            # line break(s)
            # Iterate over characters
            for c in chunk.decode(encoding):
                # Is this a line break?
                if c == sep:
                    # Give the line of text
                    yield line
                    # Reset line buffer
                    line = str()
                else:
                    # Keep building the line of text
                    # Concatenate character onto the string
                    line += c

        # Yield the last line if anything remains in the buffer and no
        # finishing line break was found
        if line:
            yield line

    @staticmethod
    def parse(lines: Iterable[str]) -> Iterable[dict]:
        """
        Process raw data and generate one dictionary per reading
        """
        # Count the total number of tables retrieved to validate
        table_count = 0
        total_table_count = 0
        col_desc = tuple()  # type: Tuple[str]

        # One item for each column
        columns = list()  # type: List[dict]
        meta = dict()  # type: Dict[str,str]
        row_count = 0
        number_of_points = 0

        for line in lines:

            # Query fail
            if line == 'mutis csvShow 0 sensors satisfy your conditions':
                return

            # Metadata comments
            if line.startswith('#'):

                if line.startswith('# Number of tables shown'):
                    total_table_count = int(line[26:])
                    # Reset counter
                    table_count = 0

                # New data set for each sensor
                elif line.startswith('# Begin CSV table'):
                    table_count += 1

                    # Reset variables
                    meta = dict()
                    columns = list()
                    number_of_points = 0
                    row_count = 0

                # Expected total row count
                elif line.startswith('# number of points:'):
                    number_of_points = int(line.partition(': ')[2])

                # Column descriptions
                elif line.startswith('# ColDescription'):
                    _, _, desc_str = line.partition(':')
                    col_desc = tuple((s.strip() for s in desc_str.split('/')))

                # Get column meta-data
                elif line.startswith('# Column_'):
                    # Skip "Column_n"
                    col_labels = line[2:].split(' / ')[1:]

                    columns.append(
                        dict(itertools.zip_longest(col_desc, col_labels)))

                elif line.startswith('# End CSV table'):

                    # Check row count
                    if row_count != number_of_points:
                        msg = 'Unexpected row count, expected {}' \
                              ' but got {}'.format(number_of_points, row_count)
                        raise ValueError(msg)

                # Other metadata
                elif line.startswith('# sensor') or line.startswith('# site'):
                    key, _, value = line[2:].partition(': ')
                    meta[key] = value

            # Skip HTML
            elif line.startswith('<'):
                continue

            # Skip blank lines
            elif line:
                # Parse a row of data
                row_count += 1
                time = None

                # Build dictionary
                values = line.split(',')

                # Check column count
                if len(values) != len(columns):
                    LOGGER.error(columns)
                    LOGGER.error(values)
                    raise ValueError('Unexpected number of data values')

                # Generate a reading for each value on this row
                for column, value in zip(columns, values):
                    # Build dimensions
                    reading = column.copy()
                    reading.update(meta)
                    reading['value'] = value

                    if reading['name'] == 'data.time':
                        time = reading['value']
                    elif reading['name'] == 'data.sensor':
                        pass
                    else:
                        if not time:
                            raise ValueError('time is %s' % time)
                        reading['time'] = time
                        yield reading

        LOGGER.info("Retrieved %s tables", table_count)
        LOGGER.info("Retrieved %s rows", row_count)

        if table_count != total_table_count:
            raise ValueError('Unexpected table count')

    @classmethod
    def parse_data_types(cls, reading: dict) -> dict:
        """
        Parse data types: values are floats
        """

        data_type = cls.DATA_TYPES.get(reading['type'], str)

        try:
            reading['value'] = data_type(reading['value'])
            reading['no-data-value'] = data_type(reading['no-data-value'])
            reading['time'] = datetime.datetime.utcfromtimestamp(
                int(reading['time']))
        except (TypeError, ValueError):
            LOGGER.error(data_type)
            LOGGER.error(reading)
            raise

        return reading

    @classmethod
    def convert_null(cls, reading: dict) -> dict:
        if reading['value'] == reading['no-data-value']:
            reading['value'] = None
        return reading

    @classmethod
    def transform(cls, reading: dict) -> dict:

        reading = cls.parse_data_types(reading)
        reading = cls.convert_null(reading)

        return reading


class UrbanFlowsQuerySSH(UrbanFlowsQuery):
    """
    Retrieve data over SSH
    """

    @staticmethod
    def _stream(*args, params: dict = None, **kwargs) -> iter:
        # Override stream method
        # Import here so dependencies aren't mandatory
        import remote

        params = params or dict()
        # Quiet output
        params['unittest'] = 's'
        # Generate arguments for command-line version of udex
        args = ' '.join(
            ("'{}={}'".format(key, value) for key, value in params.items()))

        LOGGER.debug(args)

        # Example command:
        # /home/uflo/www/cgi-bin/ufdexF1 'Tfrom=2021-01-07T09:39:57'
        # 'Tto=2021-01-07T12:39:57' 'aktion=json_META' 'freqInMin=5'
        # 'tok=generic' 'unittest=s'
        command = '/home/uflo/www/cgi-bin/ufdexF1 {args}'.format(args=args)

        username = input('Enter username for {host}: '.format(host=HOST))
        with remote.RemoteHost(host=HOST, username=username) as remote_host:
            yield from UrbanFlowsQuery.readlines(
                (remote_host.execute(command)))

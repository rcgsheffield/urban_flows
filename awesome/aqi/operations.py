import datetime
import logging

import numpy
import pandas

import ufdex
import aqi.daqi
import settings

LOGGER = logging.getLogger(__name__)


def calculate_index(row: pandas.Series) -> int:
    """
    Calculate the air quality index for a collection of readings at a certain timestamp.
    """
    # Convert to dictionary and replace numpy NaNs with None
    row = {key: None if pandas.isnull(value) else value for key, value in row.iteritems()}
    _aqi = aqi.daqi.DailyAirQualityIndex(**row)
    return _aqi.index


def get_urban_flows_data(site_id: str, start: datetime.datetime, end: datetime.datetime = None) -> pandas.DataFrame:
    LOGGER.info("Getting data for Urban Flows site '%s'", site_id)

    # Default to live data
    end = end or datetime.datetime.now(datetime.timezone.utc)

    # Get Urban Flows data
    query = ufdex.UrbanFlowsQuery(time_period=[start, end], site_ids={site_id})

    # Pre-process input data
    data = pandas.DataFrame(columns=['TIME_UTC_UNIX', 'ID_MAIN', 'site_id'])
    for row in query():
        data = data.append(row, ignore_index=True)
    data = data.rename(columns={'ID_MAIN': 'sensor', 'TIME_UTC_UNIX': 'time'})
    data = data.drop(['sensor', 'site_id'], axis=1)
    data['time'] = pandas.to_datetime(data['time'], utc=True)
    data = data.set_index('time')
    data = data.astype('float')
    data = data.sort_index()

    # There may be multiple sensors at the same site, so take an average because the time frequency of the measurements
    # will not be consistent. This smooths out the data.
    try:
        data = data.groupby(pandas.Grouper(freq=settings.AQI_TIME_AVERAGE_FREQUENCY)).mean().dropna(axis=0, how='all')
    except pandas.core.base.DataError:
        if not data.empty:
            raise

    return data


def calculate_air_quality(data: pandas.DataFrame) -> pandas.DataFrame:
    # Calculate rolling average for each pollutant
    avg = pandas.DataFrame(index=data.index)
    for uf_col, pollutant in aqi.daqi.DailyAirQualityIndex.COLUMN_MAP.items():
        window = aqi.daqi.DailyAirQualityIndex.RUNNING_AVERAGE_WINDOWS[pollutant]
        try:
            avg[pollutant] = data[uf_col].rolling(window).mean()
        except KeyError:
            avg[pollutant] = numpy.nan

    # Calculate AQI for all pollutants
    avg['air_quality_index'] = avg.apply(calculate_index, axis=1, result_type='reduce')

    return avg

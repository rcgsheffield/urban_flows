import datetime
import logging

import numpy
import pandas

import aqi.daqi
import ufdex

LOGGER = logging.getLogger(__name__)


def calculate_index(row: pandas.Series) -> int:
    """
    Calculate the air quality index for a collection of readings at a certain
    timestamp.
    """
    # Convert to dictionary and replace numpy NaNs with None
    row = {key: None if pandas.isnull(value) else value for key, value in
           row.iteritems()}
    _aqi = aqi.daqi.DailyAirQualityIndex(**row)
    return _aqi.index


def get_urban_flows_data(site_id: str, start: datetime.datetime,
                         end: datetime.datetime = None) -> pandas.DataFrame:
    LOGGER.info("Getting data for Urban Flows site '%s'", site_id)

    # Default to live data
    end = end or datetime.datetime.now(datetime.timezone.utc)

    # Get Urban Flows data
    query = ufdex.UrbanFlowsQuery(time_period=[start, end], site_ids={site_id})

    # Pre-process input data

    # Ensure consistent data frame shape
    data = pandas.DataFrame(
        columns=['time', 'sensor.id', 'UCD', 'value', 'pollutant', 'units',
                 'converted_value', 'converted_units'])

    readings = (transform(reading) for reading in query())

    # Collect data
    for reading in readings:
        data = data.append(reading, ignore_index=True)

    # Prepare data frame
    data = data.dropna(subset=['pollutant'])
    LOGGER.info("%s pollutant readings", len(data.index))
    data['time'] = pandas.to_datetime(data['time'], utc=True)
    data['value'] = data['value'].astype('float')

    if data.empty:
        return pandas.DataFrame()

    # If multiple sensors on this site, get the worst value
    s = data.groupby(['time', 'pollutant'])['converted_value'].max()
    data = s.unstack()
    data = data.sort_index()

    return data


def transform(reading: dict) -> dict:
    # Rename
    reading['pollutant'] = aqi.daqi.DailyAirQualityIndex.COLUMN_MAP.get(
        reading['UCD'])

    # Round to nearest minute because there may be multiple different sensors
    # at a site, so merge them together
    reading['time'] = reading['time'].replace(minute=0, second=0,
                                              microsecond=0)

    reading['value'] = float(reading['value'])

    reading = convert_units(reading)
    return reading


def convert_units(reading: dict) -> dict:
    try:
        func = \
        aqi.daqi.DailyAirQualityIndex.CONVERSION_FACTOR[reading['pollutant']][
            reading['units']]
        reading['converted_value'] = func(reading['value'])
        reading['converted_units'] = aqi.daqi.DailyAirQualityIndex.UNITS[
            reading['pollutant']]

    except KeyError:
        pass

    return reading


def calculate_air_quality(data: pandas.DataFrame) -> pandas.DataFrame:
    # Prepare data frame
    avg = pandas.DataFrame(index=data.index)

    # No data, abort
    if data.empty:
        return avg

    # Calculate rolling average for each pollutant
    for pollutant, values in data.iteritems():
        # Time frequency to take the rolling average
        window = aqi.daqi.DailyAirQualityIndex.RUNNING_AVERAGE_WINDOWS[
            pollutant]

        try:
            avg[pollutant] = values.rolling(window).mean()
        except KeyError:
            avg[pollutant] = numpy.nan

    # Calculate AQI for all pollutants
    avg['air_quality_index'] = avg.apply(calculate_index, axis=1,
                                         result_type='reduce')

    return avg

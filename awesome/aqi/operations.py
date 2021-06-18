import logging
from typing import Iterable

import numpy
import pandas

import aqi.daqi

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


def transform_ufo_data(readings: Iterable[dict]):
    """
    Convert Urban Flows data into standard AQI pollutants data
    """
    # Pre-process input data
    readings = (transform(reading) for reading in readings)

    data = pandas.DataFrame.from_records(
        data=readings,
        columns=['time', 'sensor.family', 'sensor.id', 'site.id', 'UCD',
                 'value', 'pollutant', 'units', 'converted_value',
                 'converted_units'])

    # Prepare data frame
    data = data.dropna(subset=['pollutant'])
    LOGGER.info("%s pollutant readings", len(data.index))
    data['time'] = pandas.to_datetime(data['time'], utc=True)
    data['value'] = data['value'].astype('float')

    # Change data shape
    # If multiple sensors on this site, get the worst value
    s = data.groupby(['site.id', 'time', 'pollutant'])['converted_value'].max()
    try:
        data = s.unstack()
    # Empty data set
    except AttributeError:
        if s.index.nlevels > 1:
            raise
        data = pandas.DataFrame()

    return data.dropna(how='all').sort_index()


def transform(reading: dict) -> dict:
    # Rename
    reading['pollutant'] = aqi.daqi.DailyAirQualityIndex.COLUMN_MAP.get(
        reading['UCD'])

    # Floor to nearest five-minute interval because there may be multiple
    # different sensors at a site, so merge them together. Also, the time
    # resolution on the Awesome portal is 5 mins
    delta = 5  # minutes
    reading['time'] = reading['time'].replace(
        minute=delta * int(reading['time'].minute / delta),
        second=0, microsecond=0
    )

    reading['value'] = float(reading['value'])

    reading = convert_units(reading)
    return reading


def convert_units(reading: dict) -> dict:
    try:
        func = aqi.daqi.DailyAirQualityIndex.CONVERSION_FACTOR[
            reading['pollutant']][reading['units']]
        reading['converted_value'] = func(reading['value'])
        reading['converted_units'] = aqi.daqi.DailyAirQualityIndex.UNITS[
            reading['pollutant']]

    except KeyError:
        pass

    return reading


def calculate_air_quality(data: pandas.DataFrame) -> pandas.Series:
    # Prepare data frame
    avg = pandas.DataFrame(index=data.index)

    # Calculate rolling average for each pollutant
    for pollutant, values in data.iteritems():
        # Get the time frequency to take the rolling average
        # Each pollutant has a different averaging period
        window = aqi.daqi.DailyAirQualityIndex.RUNNING_AVERAGE_WINDOWS[
            pollutant]

        try:
            avg[pollutant] = values.rolling(window).mean()
        except KeyError:
            avg[pollutant] = numpy.nan
        except ValueError:
            LOGGER.error("Window = %s", repr(window))
            LOGGER.error("index has %s levels", avg.index.nlevels)
            raise

    # Calculate AQI for all pollutants
    return avg.apply(calculate_index, axis=1, result_type='reduce').dropna()

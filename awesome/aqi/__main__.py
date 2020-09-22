import datetime
import logging

import numpy
import pandas

import ufdex
import aqi.daqi

LOGGER = logging.getLogger(__name__)


def calculate_index(row: pandas.Series):
    # Convert to dictionary and replace numpy NaNs with None
    row = {key: None if pandas.isnull(value) else value for key, value in row.iteritems()}
    _aqi = aqi.daqi.DailyAirQualityIndex(**row)
    return _aqi.index


def get_urban_flows_data(site_id: str, time: datetime.datetime = None) -> pandas.DataFrame:
    time = time or datetime.datetime.utcnow()

    # Get Urban Flows data
    query = ufdex.UrbanFlowsQuery(
        # Go back 24 hours
        time_period=[time - datetime.timedelta(days=1), time],
        site_ids={site_id},
    )

    # Pre-process input data
    data = pandas.DataFrame.from_dict(query())
    data = data.rename(columns={'ID_MAIN': 'sensor', 'TIME_UTC_UNIX': 'time'})
    data = data.drop(['sensor', 'site_id'], axis=1)
    data['time'] = pandas.to_datetime(data['time'], utc=True)
    data = data.set_index('time')
    data = data.astype('float')
    data = data.sort_index()

    data.info()
    print(data.head())

    # There may be multiple sensors at the same site, so take an average
    data = data.groupby(pandas.Grouper(freq='1min')).mean().dropna(axis=0, how='all')

    return data


def get_aqi(**kwargs) -> pandas.DataFrame:
    data = get_urban_flows_data(**kwargs)

    print(data.head())

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


def main():
    logging.basicConfig(level=logging.INFO)

    data = get_aqi(site_id='S0006')
    print(data.head())


if __name__ == '__main__':
    main()

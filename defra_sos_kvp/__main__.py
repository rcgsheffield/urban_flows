import argparse
import datetime
import logging
import os

import pandas

import http_session
import parsers
import mappings

DESCRIPTION = """
TODO
"""

USAGE = """
TODO
"""

LOGGER = logging.getLogger(__name__)

DATE_FORMAT = '%Y-%m-%d'

BOUNDING_BOX = (
    # Lat, long
    (53.517, -1.766),
    (53.238, -1.095),
)

STATIONS = {
    'http://environment.data.gov.uk/air-quality/so/GB_Station_GB0538A',
    'http://environment.data.gov.uk/air-quality/so/GB_Station_GB1046A',
    'http://environment.data.gov.uk/air-quality/so/GB_Station_GB1027A',
    'http://environment.data.gov.uk/air-quality/so/GB_Station_GB0037R',
    'http://environment.data.gov.uk/air-quality/so/GB_Station_GB1063A',
}


def within_bounding_box(position: tuple) -> bool:
    latitude, longitude = position

    return (BOUNDING_BOX[1][0] <= latitude <= BOUNDING_BOX[0][0]) and (
            BOUNDING_BOX[0][1] <= longitude <= BOUNDING_BOX[1][1])


def parse_date(s: str) -> datetime.date:
    t = datetime.datetime.strptime(s, DATE_FORMAT)
    return t.date()


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-d', '--date', type=parse_date, required=True, help="YY-MM-DD")
    parser.add_argument('-o', '--output', type=str, required=True, help="Output CSV file path")
    parser.add_argument('-s', '--sep', type=str, default='|', help="Output CSV separator")

    args = parser.parse_args()

    return args


def get_data(session, date: datetime.date) -> iter:
    """
    :rtype: iter[dict]
    """

    data = session.get_observation_date(date=date)

    # Serialise
    directory = 'data'
    os.makedirs(directory, exist_ok=True)
    filename = "{}.xml".format(date.isoformat())
    path = os.path.join(directory, filename)
    with open(path, 'w') as file:
        file.write(data)

        LOGGER.info("Wrote '%s'", file.name)

    parser = parsers.AirQualityParser(data)

    LOGGER.info(parser.id)

    # Iterate over observations
    for observation in parser.observations:

        for row in observation.result.iter_values():
            row['station'] = observation.station
            row['sampling_point'] = observation.sampling_point
            row['observed_property'] = observation.observed_property
            row['unit_of_measurement'] = observation.result.unit_of_measurement

            yield row


def validate(row: pandas.Series) -> bool:
    # Verified: http://dd.eionet.europa.eu/vocabulary/aq/observationverification
    if row['verification'] not in {1, 2}:
        return False

    # Validity http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity
    if row['validity'] < 0:
        return False

    return True


def parse(df: pandas.DataFrame) -> pandas.DataFrame:
    """Parse data types"""

    df['timestamp'] = pandas.to_datetime(df['timestamp'])

    data_types = dict(
        validity='int8',
        verification='uint8',
        value='float',
        sampling_point='category',
        observed_property='category',
        unit_of_measurement='category',
    )
    df = df.astype(data_types)

    return df


def transform(df: pandas.DataFrame) -> pandas.DataFrame:
    n_rows = len(df.index)

    # Filter selected stations
    df = df[df['station'].isin(STATIONS)].copy()

    df['unit_of_measurement'] = df['unit_of_measurement'].map(mappings.UNIT_MAP)
    df['observed_property'] = df['observed_property'].map(mappings.OBSERVED_PROPERTY_MAP)

    del df['StartTime']
    df = df.rename(columns={'EndTime': 'timestamp'})
    df = df.rename(columns=str.casefold)

    df = parse(df)

    # Validate
    df = df[df.apply(validate, axis=1)].copy()
    LOGGER.info("Removed %s invalid/unverified rows", n_rows - len(df.index))

    # Get station ID from station URL
    # e.g. "http://environment.data.gov.uk/air-quality/so/GB_Station_GB0037R" becomes "GB_Station_GB0037R"
    df['station'] = df['station'].apply(lambda s: s.rpartition('/')[2])

    # Output timestamp in ISO 8601
    df['timestamp'] = df['timestamp'].apply(lambda t: t.isoformat())

    # Aggregate
    df = df.groupby(['timestamp', 'station', 'observed_property', 'unit_of_measurement'])['value'].sum()

    df = df.unstack(['observed_property', 'unit_of_measurement'])

    df.columns = df.columns.map('__'.join)

    return df


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.SensorSession()
    rows = get_data(session, args.date)
    df = pandas.DataFrame.from_dict(rows)

    LOGGER.info("Retrieved %s rows", len(df.index))

    df = transform(df)

    df.to_csv(args.output, sep=args.sep)
    LOGGER.info("Wrote '%s' (%s rows)", args.output, len(df.index))


if __name__ == '__main__':
    main()

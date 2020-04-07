import argparse
import datetime
import logging

import pandas

import http_session
import parsers
import mappings
import settings
import utils
from utils import build_path

DESCRIPTION = """
This is a harvester to retrieve data from the DEFRA UK-AIR
[Sensor Observation Service](https://uk-air.defra.gov.uk/data/about_sos) via their API using the key-value pair (KVP)
binding.
"""

USAGE = """
python . --date 2020-01-01
"""

LOGGER = logging.getLogger(__name__)

DEFAULT_SEPARATOR = '|'


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)

    parser.add_argument('-v', '--verbose', action='store_true', help="Debug logging level")
    parser.add_argument('-d', '--date', type=utils.parse_date, required=True, help="YYYY-MM-DD")
    parser.add_argument('-s', '--sep', type=str, default=DEFAULT_SEPARATOR,
                        help="Output CSV separator (default: {})".format(DEFAULT_SEPARATOR))

    args = parser.parse_args()

    return args


def download_data(session, date: datetime.date, sampling_feature: str):
    data = session.get_observation_date(date=date, params={'featureOfInterest': sampling_feature})

    path = build_path(date=date, ext='xml', sub_dir='raw', suffix=sampling_feature.rpartition('/')[2])

    # Serialise
    with open(path, 'w') as file:
        file.write(data)

        LOGGER.info("Wrote '%s'", file.name)

    return data


def get_data(session, date: datetime.date, sampling_features: iter) -> iter:
    """
    :rtype: iter[dict]
    """
    for sampling_feature in sampling_features:
        data = download_data(session=session, date=date, sampling_feature=sampling_feature)

        try:
            parser = parsers.AirQualityParser(data)
        except parsers.OWSException as exc:
            LOGGER.warning(exc)
            LOGGER.warning("Skipping sampling feature")
            continue

        LOGGER.info("Feature Collection ID: %s", parser.id)

        # Iterate over observations
        for observation in parser.observations:

            LOGGER.debug("Observation ID: %s", observation.id)

            for row in observation.result.iter_values():
                # Append metadata
                row['station'] = observation.station
                row['sampling_point'] = observation.sampling_point
                row['observed_property'] = observation.observed_property
                row['unit_of_measurement'] = observation.result.unit_of_measurement

                yield row


def validate(row: pandas.Series) -> bool:
    # Check type
    if not isinstance(row, pandas.Series):
        raise TypeError(type(row))

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


def log_metadata(df):
    """Map unique properties to measurement units"""

    for station in set(df['station']):
        LOGGER.info("Station: %s", station)

    s = df[['observed_property', 'unit_of_measurement']].drop_duplicates().set_index('observed_property')[
        'unit_of_measurement']

    for prop, unit in s.iteritems():
        LOGGER.info("Observed property: %s Unit: %s", prop, unit)


def transform(df: pandas.DataFrame) -> pandas.DataFrame:
    n_rows = len(df.index)

    # Filter selected data streams
    df = df[df['sampling_point'].isin(settings.SAMPLING_FEATURES)].copy()
    LOGGER.info("Data selection: removed %s rows", n_rows - len(df.index))

    n_rows = len(df.index)

    log_metadata(df)

    # Map to UFO values
    df['unit_of_measurement'] = df['unit_of_measurement'].map(mappings.UNIT_MAP)
    df['observed_property'] = df['observed_property'].map(mappings.OBSERVED_PROPERTY_MAP)

    # Remove unnecessary column
    del df['StartTime']

    # Rename columns
    df = df.rename(columns={'EndTime': 'timestamp'})
    df = df.rename(columns=str.casefold)

    df = parse(df)

    # Validate
    valid_rows = df.apply(validate, axis=1)
    print(valid_rows)
    df = df[valid_rows].copy()
    LOGGER.info("Removed %s invalid/unverified rows", n_rows - len(df.index))

    # Get station ID from station URL by getting the final item from the URL path (after the last slash)
    # e.g. "http://environment.data.gov.uk/air-quality/so/GB_Station_GB0037R" becomes "GB_Station_GB0037R"
    df['station'] = df['station'].apply(lambda s: s.rpartition('/')[2])

    # Output timestamp in ISO 8601
    df['timestamp'] = df['timestamp'].apply(lambda t: t.isoformat())

    # One column per metric
    s = df.set_index(['timestamp', 'station', 'observed_property', 'unit_of_measurement'])['value']
    df = s.unstack(['observed_property', 'unit_of_measurement'])

    LOGGER.info("Pivoted: %s (%s rows)", df.index.names, len(df.index))

    # Flatten column headers (use only the observed property name)
    df.columns = df.columns.map(lambda t: t[0])

    # Ensure consistent data shape
    df = df.reindex(columns=settings.OUTPUT_HEADERS)

    assert not df.index.duplicated().any(), 'Duplicated index values'

    return df


def serialise(df: pandas.DataFrame, path, **kwargs):
    df.to_csv(path, **kwargs)

    LOGGER.info("Wrote '%s' (%s rows)", path, len(df.index))


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Retrieve raw data
    session = http_session.SensorSession()
    rows = get_data(session=session, date=args.date, sampling_features=settings.SAMPLING_FEATURES)
    df = pandas.DataFrame.from_dict(rows)

    LOGGER.info("Retrieved %s rows", len(df.index))

    # Clean data
    df = transform(df)

    path = build_path(date=args.date, ext='csv', sub_dir='todb')
    serialise(df, path=path)


if __name__ == '__main__':
    main()

import argparse
import datetime
import logging
import csv

import http_session
import parsers
import mappings
import settings
import utils
import metadata

from collections import OrderedDict

DESCRIPTION = """
This is a harvester to retrieve data from the DEFRA UK-AIR Sensor Observation Service via their API using the key-value
pair (KVP) binding.

https://uk-air.defra.gov.uk/data/about_sos
"""

USAGE = """
python . --date 2020-01-01
"""

LOGGER = logging.getLogger(__name__)


class UrbanDialect(csv.excel):
    """CSV output format for the Urban Flows Observatory"""
    delimiter = settings.DEFAULT_SEPARATOR


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)

    parser.add_argument('-v', '--verbose', action='store_true', help="Debug logging level")
    parser.add_argument('-d', '--date', type=utils.parse_date, required=True, help="YYYY-MM-DD")
    parser.add_argument('-r', '--raw', help="Raw data storage directory", default=settings.DEFAULT_RAW_DIR)
    parser.add_argument('-o', '--output', help="Output (clean) data file path", required=True)

    args = parser.parse_args()

    return args


def store_raw_data(sampling_feature, date, directory, data):
    suffix = sampling_feature.rpartition('/')[2]
    path = utils.build_path(date=date, ext='xml', directory=directory, suffix=suffix)

    # Serialise
    with open(path, 'w') as file:
        file.write(data)

        LOGGER.debug("Wrote '%s'", file.name)


def download_data(session, date: datetime.date, sampling_feature: str, directory: str):
    data = session.get_observation_by_date(date=date, params={'featureOfInterest': sampling_feature})
    store_raw_data(sampling_feature=sampling_feature, date=date, directory=directory, data=data)

    return data


def get_data(session, date: datetime.date, sampling_features: iter, directory: str) -> iter:
    """
    :rtype: iter[OrderedDict]
    """
    n = 0

    for sampling_feature in sampling_features:
        data = download_data(session=session, date=date, sampling_feature=sampling_feature, directory=directory)

        try:
            parser = parsers.AirQualityParser(data)
        except parsers.OWSException as exc:
            LOGGER.warning(exc)
            LOGGER.warning("Skipping sampling feature")
            continue

        LOGGER.debug("Feature Collection ID: %s", parser.id)

        # Iterate over observations
        for observation in parser.observations:

            LOGGER.debug("Observation ID: %s", observation.id)

            for row in observation.result.iter_values():
                # Append metadata
                row['station'] = observation.station
                row['sampling_point'] = observation.sampling_point
                row['observed_property'] = observation.observed_property
                row['feature_of_interest'] = observation.feature_of_interest
                row['unit_of_measurement'] = observation.result.unit_of_measurement

                yield row

                LOGGER.debug(row)

                n += 1

    LOGGER.info("Retrieved %s rows of data", n)


def validate(row: OrderedDict) -> bool:
    # Verified: http://dd.eionet.europa.eu/vocabulary/aq/observationverification
    if row['verification'] not in {1, 2}:
        return False

    # Validity http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity
    if row['validity'] < 0:
        return False

    return True


def filter_n(function, iterable) -> iter:
    """Filter and count the number of rows"""
    n_pass, n_fail = 0, 0

    for item in iterable:
        if function(item):
            yield item
            n_pass += 1
        else:
            n_fail += 1

    LOGGER.info("Filter %s: output %s rows (dropped %s rows)", function.__name__, n_pass, n_fail)


def parse(row: OrderedDict) -> OrderedDict:
    """Parse data types"""

    data_types = dict(
        validity=int,
        verification=int,
        value=float,
        timestamp=utils.parse_timestamp,
    )

    # Cast to new data type (or default to string)
    _row = OrderedDict()

    for key, value in row.items():
        DataType = data_types.get(key, str)

        _row[key] = DataType(value)

    return _row


def transform_row(row: OrderedDict) -> OrderedDict:
    # Map to UFO values
    row['unit_of_measurement'] = mappings.UNIT_MAP[row['unit_of_measurement']]
    row['observed_property'] = mappings.OBSERVED_PROPERTY_MAP[row['observed_property']]

    # Remove unnecessary column
    del row['StartTime']

    # Rename columns
    row['timestamp'] = row.pop('EndTime')

    # Lower case keys
    row = OrderedDict(((key.casefold(), value) for key, value in row.items()))

    row['station'] = metadata.clean_station_id(row['station'])

    return row


def filter_row(row: OrderedDict) -> bool:
    """Filter selected data streams"""

    return row['feature_of_interest'] in settings.SAMPLING_FEATURES


def transform(rows: iter) -> iter:
    for row in rows:
        row = transform_row(row)
        row = parse(row)

        yield row


def pivot(rows: iter) -> iter:
    _rows = OrderedDict()

    headers = settings.OUTPUT_HEADERS
    default = {key: None for key in headers}

    n0 = 0
    for row in rows:
        key = (row['timestamp'], row['station'])

        try:
            _row = _rows[key]
        except KeyError:
            # Initialise new row
            _row = default.copy()
            _row['timestamp'] = row['timestamp']
            _row['sensor'] = row['station']

            _rows[key] = _row

        _row[row['observed_property']] = row['value']

        n0 += 1

    n1 = len(_rows)
    LOGGER.info("Pivoted: reduced %s input rows to %s output rows", n0, n1)

    return _rows.values()


def sort(rows: iter, key='timestamp') -> iter:
    yield from sorted(rows, key=lambda row: row[key])


def serialise(rows, path, **kwargs):
    """Write to CSV file"""

    fieldnames = settings.OUTPUT_HEADERS

    LOGGER.info("Writing CSV with headers: %s", fieldnames)

    with open(path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, dialect=UrbanDialect, **kwargs)

        n = 0
        for row in rows:
            LOGGER.debug(row)
            # Output timestamp in ISO 8601
            row['timestamp'] = row['timestamp'].isoformat()

            writer.writerow(row)

            n += 1

        LOGGER.info("Wrote %s rows to '%s'", n, file.name)


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Retrieve raw data
    session = http_session.SensorSession()
    LOGGER.info('Retrieving raw data and storing in %s', args.raw)
    rows = get_data(session=session, date=args.date, sampling_features=settings.SAMPLING_FEATURES, directory=args.raw)

    # Clean data
    rows = filter_n(filter_row, rows)
    rows = transform(rows)
    rows = filter_n(validate, rows)
    rows = pivot(rows)
    rows = sort(rows)

    serialise(rows, path=args.output)


if __name__ == '__main__':
    main()

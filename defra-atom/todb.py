"""
Prepare data to be converted into NetCDF format.
"""

import logging
import argparse
import pathlib
import os.path

import pandas as pd

import settings
import utils

LOGGER = logging.getLogger(__name__)


def convert_units(df: pd.DataFrame) -> pd.DataFrame:
    """Change units of measurement from source to destination standards"""

    rename = dict()

    for col, s in df.iteritems():
        (observed_property, unit_of_measurement) = col

        try:
            conversion = settings.UNIT_MAP[unit_of_measurement][observed_property]
        except KeyError:
            LOGGER.error(col)
            raise

        # Map column names
        rename[col] = conversion['label']

        # Calculate conversion
        factor = float(conversion['factor'])
        s = s.mul(factor)

        df[col] = s

    df = df.rename(columns=rename, errors='raise')

    return df


def url_id(url: str) -> str:
    """Get the final part (identifier) from a spatial object URL"""
    return url.split('/')[-1]


def transform(df: pd.DataFrame) -> pd.DataFrame:
    # Use ending timestamp as the timestamp
    del df['StartTime']
    df = df.rename(columns={'EndTime': 'timestamp'})

    # Get the final part (identifier) from the sampling point (sensor) URL
    df['sensor'] = df['sampling_point'].map(url_id)
    df['site'] = df['station'].map(url_id)

    # Aggregate
    df = df.groupby(['timestamp', 'site', 'observed_property', 'unit_of_measurement'])[
        'Value'].first().unstack().unstack().swaplevel(axis=1)

    # Flatten multi-level index into a flat index formed of two-tuples
    df.columns = list(df.columns)

    df = convert_units(df)

    return df


def build_output_dir(root_output_dir: str, year, input_path, date: str) -> str:
    output_dir = utils.build_output_dir(root_output_dir, year, input_path)
    # Create a subdirectory for each date
    output_dir = os.path.join(output_dir, *date.split('-'))

    os.makedirs(output_dir, exist_ok=True)

    return output_dir


def configure_arguments():
    """Command-line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', default=settings.DEFAULT_CLEAN_DIR, type=str, help="Input file directory")
    parser.add_argument('-o', '--output', default=settings.DEFAULT_DB_DIR, type=str, help="Output file directory")
    parser.add_argument('-y', '--year', required=True, type=int, help="Year time filter")
    parser.add_argument('-v', '--verbose', action='store_true', help="Debug logging mode")

    # CSV output options
    parser.add_argument('-s', '--sep', default='|', type=str, help="Output CSV separator")
    parser.add_argument('-c', '--header', default=False, action='store_true',
                        help="If true, write column headers in CSV output")

    return parser.parse_args()


def main():
    args = configure_arguments()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Iterate over input files
    input_dir = utils.build_input_dir(args.input, args.year)

    # Loop over input files
    for input_path in pathlib.Path(input_dir).glob('*/*.csv'):
        df = pd.read_csv(input_path)
        LOGGER.debug("Read '%s'", input_path)
        df = transform(df)

        if df.empty:
            LOGGER.warning("Empty data set %s", input_path)
        else:
            LOGGER.info("HEADERS: %s", list(df.columns))

        # For the multi-level index, which level contains the timestamp?
        level = df.index.names.index('timestamp')

        # Partition by date (extract date from ISO timestamp)
        for date, chunk in df.groupby(by=lambda idx: idx[level][:10]):
            # Build output path
            output_dir = build_output_dir(args.output, args.year, input_path, date)
            output_path = utils.build_output_path(output_dir, input_path)

            # Serialise output
            with open(output_path, 'x', newline='') as output_file:
                chunk.to_csv(output_file, sep=args.sep, header=args.header)

                LOGGER.info("Wrote '%s'", output_file.name)


if __name__ == '__main__':
    main()

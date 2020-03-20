"""
Clean data
"""

import logging
import pathlib
import argparse
import os.path
import csv
import datetime

import settings
import utils

LOGGER = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Data Validation Error"""
    pass


def parse_timestamp(timestamp: str) -> datetime.datetime:
    try:
        t = datetime.datetime.fromisoformat(timestamp[:-1])

    # The hour is "24" (instead of "00")
    except ValueError:
        date = datetime.date.fromisoformat(timestamp[:10])
        time = datetime.time.min
        t = datetime.datetime.combine(date, time)

    return t.replace(tzinfo=datetime.timezone.utc)


def validate(row) -> bool:
    # Verified: http://dd.eionet.europa.eu/vocabulary/aq/observationverification
    if row['Verification'] not in {'1', '2'}:
        raise ValidationError('Unverified data', row)

    # Validity http://dd.eionet.europa.eu/vocabulary/aq/observationvalidity
    if int(row['Validity']) < 0:
        raise ValidationError('Invalid data', row)

    return True


def transform(row: dict) -> dict:
    """Clean a row of data"""

    # Parse timestamps
    for key in {'StartTime', 'EndTime'}:
        row[key] = parse_timestamp(row[key]).isoformat()

    validate(row)

    return row


def configure_arguments():
    """Command-line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', default=settings.DEFAULT_STAGE_DIR, type=str, help="Input file directory")
    parser.add_argument('-o', '--output', default=settings.DEFAULT_CLEAN_DIR, type=str, help="Output file directory")
    parser.add_argument('-y', '--year', required=True, type=int, help="Year time filter")
    parser.add_argument('-v', '--verbose', action='store_true', help="Debug logging mode")

    return parser.parse_args()


def main():
    args = configure_arguments()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Load input files
    input_dir = os.path.join(args.input, str(args.year))
    for input_path in pathlib.Path(input_dir).glob('*/*.csv'):
        with open(input_path) as file:
            LOGGER.debug("Reading '%s'...", file.name)

            reader = csv.DictReader(file)

            # CSV output
            output_dir = utils.build_output_dir(args.output, args.year, input_path)
            output_path = utils.build_output_path(output_dir, input_path)
            with open(output_path, 'x', newline='') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=settings.FIELD_NAMES)
                writer.writeheader()

                # Iterate over rows of data
                for row in reader:
                    try:
                        row = transform(row)

                    # Skip invalid rows
                    except ValidationError:
                        LOGGER.warning("INVALID: %s", row)
                        continue

                    writer.writerow(row)

                LOGGER.info("Wrote '%s'", output_file.name)


if __name__ == '__main__':
    main()

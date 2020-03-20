"""
Convert XML to CSV data
"""

import logging
import pathlib
import argparse
import os.path
import csv

import settings
import parsers.inspire
import parsers.exceptions
import utils

DESCRIPTION = """
Iterate over downloaded XML files and convert to CSV format.
"""

LOGGER = logging.getLogger(__name__)


def configure_arguments():
    """Command-line arguments"""

    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-i', '--input', default=settings.DEFAULT_RAW_DIR, type=str, help="Input file directory")
    parser.add_argument('-o', '--output', default=settings.DEFAULT_STAGE_DIR, type=str, help="Output file directory")
    parser.add_argument('-y', '--year', required=True, type=int, help="Year time filter")
    parser.add_argument('-v', '--verbose', action='store_true', help="Debug logging mode")

    return parser.parse_args()


def get_writer(file, fieldnames):
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    return writer


def change_file_extension(path: str, new_ext: str = '.csv') -> str:
    """Change file extension to .csv)"""

    filename, ext = os.path.splitext(os.path.basename(path))
    filename += new_ext

    return os.path.join(os.path.dirname(path), filename)


def main():
    args = configure_arguments()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # Iterate over input data
    input_dir = os.path.join(args.input, str(args.year))
    for input_path in pathlib.Path(input_dir).glob('*/*.xml'):
        with open(input_path) as input_file:
            LOGGER.debug("Read '%s'", input_file.name)

            # Build output path
            output_dir = utils.build_output_dir(args.output, args.year, input_path)
            output_path = change_file_extension(utils.build_output_path(output_dir, input_path))

            # CSV output
            with open(output_path, 'x', newline='') as output_file:
                writer = get_writer(output_file, settings.FIELD_NAMES)

                # Parse XML data
                data_parser = parsers.inspire.AirQualityParser(input_file.read())

                # Loop over observations (data collections)
                for observation in data_parser.observations:

                    # If this item doesn't have the required metadata then skip it
                    try:
                        rows = observation.iter_values()
                        writer.writerows(rows)
                    except parsers.exceptions.MissingMetadataError:
                        LOGGER.warning("Missing metadata, skipping %s", observation.id)
                        continue

                    LOGGER.debug('Converted %s to CSV format', observation.id)

                LOGGER.info("Wrote '%s'", output_file.name)


if __name__ == '__main__':
    main()

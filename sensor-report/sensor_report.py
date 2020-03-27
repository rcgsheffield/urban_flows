import logging
import argparse

from data_service.handler import DataHandler

LOGGER = logging.getLogger(__name__)

USAGE = """
$ python sensor_report.py --input my_sensor_data.csv --output my_report.csv
"""

DESCRIPTION = """
Reads the input data and provides a report of the sensor up-time.

It loads the data from the input directory/file and outputs a report CSV file. 
"""

DEFAULT_AMBER_THRESHOLD = 0.8


def get_args():
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)

    parser.add_argument("-i", dest="input", help="The input file or path", required=False, default="./data/")
    parser.add_argument("-o", dest="output", help="The csv output path", required=False,
                        default="./data/output/report.csv")
    parser.add_argument("-t", dest="amber_threshold", help="Theshold for amber status", required=False, type=float,
                        default=DEFAULT_AMBER_THRESHOLD)

    args = parser.parse_args()

    return args


def main():
    args = get_args()
    logging.basicConfig(level=logging.INFO)

    data_handler = DataHandler(args.input, args.output)
    data_handler.process_input()
    data_handler.create_report(amber_threshold=args.amber_threshold)


if __name__ == '__main__':
    main()

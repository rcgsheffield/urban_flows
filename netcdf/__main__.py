import argparse
import logging
import itertools
import json
from typing import Iterable
from collections import OrderedDict

from netCDF4 import Dataset

import remote

LOGGER = logging.getLogger(__name__)

REMOTE_HOST = 'ufdev.shef.ac.uk'


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-u', '--username', help='Username on remote host', required=True)
    parser.add_argument('-t', '--timeout', type=int, help='time in milliseconds for how long a blocking call may wait')
    parser.add_argument('-r', '--host', default=REMOTE_HOST, help='Remote host name')
    parser.add_argument('-p', '--port', type=int, default=22)
    return parser.parse_args()


def get_data_files(host: remote.RemoteHost) -> Iterable[bytes]:
    """
    Retrieve binary data files from remote host
    """

    # Get full paths of all netCDF files
    paths = str().join(host.execute_decode('ls -d /home/uflo/data/dbData/**/**/**/*.nc'))
    for path in paths.split():
        LOGGER.info(path)

        # Save remote data to memory as binary object
        yield bytes().join(host.execute('cat {}'.format(path)))


def get_datasets(host) -> Iterable[Dataset]:
    """
    Load netCDF files using API
    """
    for buffer in get_data_files(host):
        # Create data set in memory (don't store to disk)
        with Dataset('in-mem-file', mode='r', memory=buffer) as dataset:
            # Show metadata
            LOGGER.info("Metadata: %s", json.dumps(dataset.__dict__))
            LOGGER.info('Dimensions: %s', json.dumps(list(dataset.dimensions.keys())))
            LOGGER.info('Variables: %s', json.dumps(list(dataset.variables.keys())))

            dtypes = {name: var.dtype for name, var in dataset.variables.items()}
            LOGGER.info('Data types: %s', dtypes)

            yield dataset


def get_data_rows(host) -> Iterable[OrderedDict]:
    """
    Convert netCDF data sets into multiple dictionaries (one dictionary per row)
    """
    for dataset in get_datasets(host):
        # Column headers (variable names)
        headers = dataset.variables.keys()

        # Build rows of data (one dictionary per row)
        row_count = 0
        for values in itertools.zip_longest(*dataset.variables.values()):
            row = OrderedDict(zip(headers, values))
            yield row
            row_count += 1

        LOGGER.info("Generated %s rows", row_count)


def write_csv(rows: Iterable[dict]):
    """
    Export dictionaries to CSV data format
    """

    import csv
    import sys

    writer = None

    def get_writer():
        nonlocal row
        _writer = csv.DictWriter(sys.stdout, row.keys())
        _writer.writeheader()
        return _writer

    for row in rows:
        writer = writer or get_writer()
        try:
            writer.writerow(row)

        # New data set (different headers)
        except ValueError:
            writer = get_writer()
            writer.writerow(row)


def numpy_to_native(row: dict) -> Iterable[tuple]:
    """
    Convert Numpy data types to Python natives ones
    """
    for key, value in row.items():
        try:
            value = value.item()
            yield key, value
        except ValueError:
            # numpy.dtype('S1') -> list[bytes] -> list[str]
            yield key, [b.decode() for b in value]


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with remote.RemoteHost(args.host, args.port, username=args.username, timeout=args.timeout) as host:
        for row in get_data_rows(host):
            try:
                # Convert to Python native data type
                row = dict(numpy_to_native(row))
            except (ValueError, TypeError) as exc:
                LOGGER.error(exc)
                LOGGER.error(row)
                raise
            print(json.dumps(row))


if __name__ == '__main__':
    main()

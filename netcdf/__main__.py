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


def get_data(host: remote.RemoteHost) -> Iterable[OrderedDict]:
    # Get full paths of all netCDF files
    for path in host.execute_decode_lines('ls -d /home/uflo/data/dbData/**/**/**/*.nc'):
        LOGGER.info(path)

        # Save remote data to memory as binary object
        buffer = bytes().join(host.execute('cat {}'.format(path)))

        # Create data set
        dataset = Dataset('in-mem-file', mode='r', memory=buffer)

        # Show metadata
        LOGGER.info("Metadata: %s", json.dumps(dataset.__dict__))
        LOGGER.info('Dimensions: %s', json.dumps(list(dataset.dimensions.keys())))

        # Column headers (variable names)
        keys = dataset.variables.keys()

        row_count = 0
        for values in tuple(itertools.zip_longest(*dataset.variables.values())):
            row = OrderedDict(zip(keys, values))
            yield row
            row_count += 1

        LOGGER.info("Generated %s rows", row_count)


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with remote.RemoteHost(args.host, args.port, username=args.username, timeout=args.timeout) as host:
        for _ in get_data(host):
            pass


if __name__ == '__main__':
    main()

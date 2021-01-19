import argparse
import logging
import itertools
import json
from collections import OrderedDict

import netCDF4

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


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    with remote.RemoteHost(args.host, args.port, username=args.username, timeout=args.timeout) as host:
        # Get full paths of all netCDF files
        for path in itertools.islice(host.execute_decode_lines('ls -d /home/uflo/data/dbData/**/**/**/*.nc'), 1, 2):
            LOGGER.info(path)

            # Save remote data to memory as binary object
            buffer = bytes().join(host.execute('cat {}'.format(path)))

            # Create data set
            dataset = netCDF4.Dataset('in-mem-file', mode='r', memory=buffer)

            # Show metadata
            LOGGER.info("Metadata: %s", json.dumps(dataset.__dict__))
            LOGGER.info('Dimensions: %s', json.dumps(list(dataset.dimensions.keys())))

            keys = dataset.variables.keys()

            for values in tuple(itertools.zip_longest(*dataset.variables.values())):
                row = OrderedDict(zip(keys, values))

                print(row)

if __name__ == '__main__':
    main()

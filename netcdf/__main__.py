import argparse
import logging

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
        for path in host.execute_decode_lines('ls -d /home/uflo/data/dbData/**/**/**/*.nc'):
            LOGGER.info(path)

            # Save remote data to memory as binary object
            buffer = bytes().join(host.execute('cat {}'.format(path)))

            # Create data set
            dataset = netCDF4.Dataset('in-mem-file', mode='r', memory=buffer)
            LOGGER.info(dataset)
            break


if __name__ == '__main__':
    main()

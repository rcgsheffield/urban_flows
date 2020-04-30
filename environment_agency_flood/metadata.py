import logging
import argparse

import http_session
import objects

DESCRIPTION = """
Get station and measure information.
"""

USAGE = """
Specify either --stations or --measures
"""

LOGGER = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)

    parser.add_argument('-s', '--stations', action='store_true', help='List stations')
    parser.add_argument('-m', '--measures', action='store_true', help='List measures')
    parser.add_argument('-l', '--lat', help='Latitude', type=float, default=53.37)
    parser.add_argument('-o', '--long', help='Longitude', type=float, default=-1.47)
    parser.add_argument('-d', '--dist', help='Distance (km)', type=int, default=30)
    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')

    return parser, parser.parse_args()


def main():
    parser, args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.FloodSession()

    # Ensure correct input
    if not (args.measures or args.stations):
        parser.print_help()
        exit()

    # Build unique list of measures
    measure_ids = set()

    # Iterate over stations
    for station in objects.Station.list(session, lat=args.lat, long=args.long, dist=args.dist):
        if args.stations:
            print(station['@id'])
        elif args.measures:
            for measure in station['measures']:
                measure_id = measure['@id']
                if measure_id not in measure_ids:
                    measure_ids.add(measure_id)
                    print(measure_id)
        else:
            raise ValueError('No option specified')


if __name__ == '__main__':
    main()

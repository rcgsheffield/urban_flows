import argparse
import logging

import assets
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

    parser.add_argument('-i', '--station_ids', action='store_true', help='List stations')
    parser.add_argument('-m', '--measures', action='store_true', help='List measures')
    parser.add_argument('-l', '--lat', help='Latitude', type=float, default=53.37)
    parser.add_argument('-o', '--long', help='Longitude', type=float, default=-1.47)
    parser.add_argument('-d', '--dist', help='Distance (km)', type=int, default=30)
    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-s', '--sites', action='store_true', help='Generate Urban Flows metadata files')
    parser.add_argument('-n', '--sensors', action='store_true', help='Generate Urban Flows metadata files')

    return parser, parser.parse_args()


def print_measures(measures):
    """Print unique measures"""
    measure_ids = set()

    for measure in measures:
        measure_id = measure['@id']
        if measure_id not in measure_ids:
            measure_ids.add(measure_id)
            print(measure_id)

    return measure_ids


def station_to_site(station: dict) -> assets.Site:
    """Map station data to Urban Flows station metadata"""

    return assets.Site(
        site_id=station['stationReference'],
        latitude=station['lat'],
        longitude=station['long'],
        address=station.get('riverName'),
        desc_url=station['@id'],
        first_date=station.get('dateOpened'),
        city=station.get('town'),
        country='United Kingdom',
    )


def station_to_sensor(station: dict) -> assets.Sensor:
    """Map station data to Urban Flows station metadata"""

    return assets.Sensor(
        sensor_id=station['stationReference'],
        family='Environment Agency Flood',
        detectors=[
            dict(name=measure['parameter'], unit=measure['unitName'], id=measure['@id'])
            for measure in station['measures']
        ],
        desc_url=station['@id'],
        first_date=station.get('dateOpened'),
    )


def main():
    parser, args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.FloodSession()

    # Iterate over stations
    for station in objects.Station.list(session, lat=args.lat, long=args.long, dist=args.dist):
        if args.station_ids:
            print(station['@id'])
        elif args.measures:
            print_measures(station['measures'])
        elif args.sites:
            print(station_to_site(station))
        elif args.sensors:
            print(station_to_sensor(station))
        else:
            parser.print_help()


if __name__ == '__main__':
    main()

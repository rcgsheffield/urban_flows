import argparse
import logging
import json

import assets
import http_session
import objects
import settings

DESCRIPTION = """
Get information about all stations within the specified geographical area defined by the longitude, latitude and the
distance from that point.

This script may be run in several modes: either to retrieve a list of Environment Agency stations or to convert those
into Urban Flows Observatory assets (Sites and Sensors). 
"""

USAGE = """
python metadata.py --sites
python metadata.py --sensors
"""

LOGGER = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)

    parser.add_argument('-i', '--station_ids', action='store_true', help='List stations')
    parser.add_argument('-m', '--measures', action='store_true', help='List measures')
    parser.add_argument('-l', '--lat', help='Latitude', type=float, default=settings.DEFAULT_LATITUDE)
    parser.add_argument('-o', '--long', help='Longitude', type=float, default=settings.DEFAULT_LONGITUDE)
    parser.add_argument('-d', '--dist', help='Distance (km)', type=int, default=settings.DEFAULT_DISTANCE)
    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-s', '--sites', action='store_true', help='Generate Urban Flows metadata files')
    parser.add_argument('-n', '--sensors', action='store_true', help='Generate Urban Flows metadata files')
    parser.add_argument('-c', '--csv', action='store_true', help='Show CSV headers')

    return parser, parser.parse_args()


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

    if args.csv:
        print(settings.UrbanDialect.delimiter.join(settings.HEADERS))
    elif args.station_ids or args.measures or args.sites or args.sensors:
        measures = set()

        # Iterate over stations
        for station in objects.Station.list(session, lat=args.lat, long=args.long, dist=args.dist):
            # List station Ids
            if args.station_ids:
                print(station['@id'])

            # List measure IDs
            elif args.measures:
                # Print unique measures
                measures.update((measure['@id'] for measure in station['measures']))
                for measure in measures:
                    print(measure)

            # Get UFO assets
            elif args.sites:
                print(station_to_site(station))
            elif args.sensors:
                print(station_to_sensor(station))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

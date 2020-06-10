import argparse
import logging

import ufmetadata.assets

import settings
import http_session
import parsers
import mappings

DESCRIPTION = """
Build metadata for the Urban Flows Observatory asset registry.
"""

USAGE = """
python metadata.py --meta
"""

LOGGER = logging.getLogger(__name__)


class MissingConceptError(KeyError):
    """This item doesn't exist in the concept mapping"""
    pass


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-s', '--sampling', action='store_true', help='List sampling points')
    parser.add_argument('-f', '--features', action='store_true', help='List features of interest')
    parser.add_argument('-m', '--meta', action='store_true', help='Get metadata objects')
    parser.add_argument('-r', '--region', type=int, default=settings.REGION_OF_INTEREST, help='Region of interest')

    args = parser.parse_args()

    return parser, args


def clean_station_id(station_id: str) -> str:
    """Remove redundant part of station identifier string"""
    return station_id.partition('Station_GB')[2]


def build_site(station: parsers.Station) -> ufmetadata.assets.Site:
    return ufmetadata.assets.Site(
        site_id=clean_station_id(station.id),
        latitude=station.coordinates[0],
        longitude=station.coordinates[1],
        altitude=station.coordinates[2],
        address=station.name,
        city=station.name,
        desc_url=station.info,
        country=settings.COUNTRY,
        postcode=None,
        first_date=station.start_time,
        operator=dict(url=station.belongs_to),
    )


def build_detector(sampling_point: parsers.SamplingPoint) -> dict:
    LOGGER.debug(sampling_point.url)

    observed_property = sampling_point.observed_property
    try:
        name = mappings.OBSERVED_PROPERTY_MAP[observed_property]
    except KeyError:
        pollutant_id = int(observed_property.rpartition('/')[2])
        if pollutant_id >= 10000000:
            name = mappings.MISSING
        else:
            raise MissingConceptError(observed_property)

    return dict(
        name=name,
        # TODO automate getting units
        unit='?',
        epsilon='?',
    )


def build_sensor(station: parsers.Station, sampling_points: iter) -> ufmetadata.assets.Sensor:
    return ufmetadata.assets.Sensor(
        sensor_id=clean_station_id(station.id),
        family=settings.FAMILY,
        detectors=[build_detector(sp) for sp in sampling_points],
        first_date=station.start_time,
        desc_url=station.info,
        provider=dict(name='Department for Environment, Food and Rural Affairs'),
    )


def get_stations(session, sampling_point_urls: set) -> dict:
    """Get unique stations by iterating over sampling points"""

    LOGGER.info("Retrieving station information...")
    stations = dict()

    for sampling_point_url in sampling_point_urls:
        LOGGER.debug("Sampling point %s", sampling_point_url)
        data = parsers.SpatialObject.get(session=session, url=sampling_point_url)
        parser = parsers.AirQualityParser(data)

        for sampling_point in parser.sampling_points:
            station_url = sampling_point.broader
            data = parsers.Station.get(session=session, url=station_url)
            parser = parsers.AirQualityParser(data)

            for station in parser.stations:
                LOGGER.debug("Station ID: %s", station.id)
                try:
                    stations[station_url]['sampling_points'][sampling_point_url] = sampling_point
                except KeyError:
                    stations[station_url] = dict(
                        station=station,
                        sampling_points={sampling_point_url: sampling_point}
                    )

    return stations


def get_metadata(stations):
    """Make asset configuration files"""
    # Iterate over stations
    for station_url, station_meta in stations.items():
        station = station_meta['station']
        LOGGER.info("Station: %s %s", station, station.coordinates)

        # Site
        site = build_site(station)
        site.save()

        # Sensor
        sampling_points = station_meta['sampling_points'].values()
        sensor = build_sensor(station, sampling_points)
        sensor.save()


def main():
    parser, args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.sampling or args.features:
        with http_session.DefraMeta() as session:
            if args.sampling:
                print(session.get_sampling_points_by_region(args.region))
            elif args.features:
                print(session.get_features_of_interest_by_region(args.region))

    elif args.meta:

        with http_session.DefraMeta() as meta_session:
            sampling_point_urls = meta_session.get_sampling_points_by_region(region_id=args.region)

        with http_session.SensorSession() as session:
            stations = get_stations(session=session, sampling_point_urls=sampling_point_urls)
            get_metadata(stations=stations)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

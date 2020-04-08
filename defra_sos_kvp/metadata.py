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
python metadata.py
"""

LOGGER = logging.getLogger(__name__)


def get_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION, usage=USAGE)

    parser.add_argument('-v', '--verbose', action='store_true', help='Debug logging')
    parser.add_argument('-s', '--sampling', action='store_true', help='List sampling points')
    parser.add_argument('-m', '--meta', action='store_true', help='Get metadata objects')

    args = parser.parse_args()

    return parser, args


def get_sampling_points_by_region(region_id):
    session = http_session.DefraMeta()

    sampling_points = set()

    for group_id, group in session.groups.items():

        LOGGER.info("Group %s: %s", group_id, group[0])

        for site in session.site_processes(region_id, group_id=group_id):
            LOGGER.debug("%s: %s", site['site_name'], site['station_identifier'])

            for parameter in site['parameter_ids']:
                sampling_point = parameter['sampling_point']
                sampling_points.add(sampling_point)

    return sampling_points


def build_site(station: parsers.Station) -> ufmetadata.assets.Site:
    site = ufmetadata.assets.Site(
        site_id=station.id,
        latitude=station.coordinates[0],
        longitude=station.coordinates[1],
        altitude=station.coordinates[2],
        address=station.name,
        city=station.name,
        desc_url=station.info,
        country='United Kingdom',
        postcode=None,
        first_date=station.start_time,
        operator=dict(url=station.belongs_to),
    )

    return site


def build_detector(sampling_point: parsers.SamplingPoint) -> dict:
    return dict(
        name=mappings.OBSERVED_PROPERTY_MAP[sampling_point.observed_property],
        # TODO automate getting units
        unit='?',
        epsilon='?',
    )


def build_sensor(station: parsers.Station, sampling_points: iter) -> ufmetadata.assets.Sensor:
    sensor = ufmetadata.assets.Sensor(
        sensor_id=station.id,
        family='DEFRA',
        detectors=list(map(build_detector, sampling_points)),
        first_date=station.start_time,
        desc_url=station.info,
        provider=dict(
            name='Department for Environment, Food and Rural Affairs'
        ),
    )

    return sensor


def get_stations(session, sampling_point_urls: set) -> dict:
    stations = dict()

    for sampling_point_url in sampling_point_urls:

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
                        sampling_points={
                            sampling_point_url: sampling_point,
                        }
                    )

    return stations


def get_metadata():
    session = http_session.SensorSession()
    stations = get_stations(session=session, sampling_point_urls=settings.SAMPLING_FEATURES)

    for station_url, station_meta in stations.items():
        station = station_meta['station']

        LOGGER.info("Station: %s %s", station, station.coordinates)

        site = build_site(station)
        site.save()

        sampling_points = station_meta['sampling_points'].values()
        sensor = build_sensor(station, sampling_points)
        sensor.save()


def main():
    parser, args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if args.sampling:
        print(get_sampling_points_by_region(settings.REGION_OF_INTEREST))
    elif args.meta:
        get_metadata()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

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
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    return args


def build_site(station: parsers.Station) -> ufmetadata.assets.Site:
    site = ufmetadata.assets.Site(
        site_id=station.id,
        latitude=station.coordinates[0],
        longitude=station.coordinates[1],
        altitude=station.altitude['value'],
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
    )


def build_sensor(station: parsers.Station, sampling_points: iter) -> ufmetadata.assets.Sensor:
    sensor = ufmetadata.assets.Sensor(
        sensor_id=station.id,
        family='Department for Environment, Food and Rural Affairs',
        detectors=map(build_detector, sampling_points),
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


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.SensorSession()
    stations = get_stations(session=session, sampling_point_urls=settings.SAMPLING_POINTS)

    for station_url, station_meta in stations.items():
        station = station_meta['station']

        site = build_site(station)
        site.save()

        sampling_points = station_meta['sampling_points'].values()
        sensor = build_sensor(station, sampling_points)
        sensor.save()


if __name__ == '__main__':
    main()

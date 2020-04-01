import argparse
import logging

import settings
import http_session
import parsers
import ufmetadata.assets

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


def build_sensor(station: parsers.Station) -> ufmetadata.assets.Sensor:
    sensor = ufmetadata.assets.Sensor(
        sensor_id=station.id,
        family='Department for Environment, Food and Rural Affairs',
        detectors=[
            dict(name='', unit='', epsilon='', ),
        ]
    )

    return sensor


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.SensorSession()

    for station_url in settings.STATIONS:
        LOGGER.info(station_url)

        data = parsers.Station.get(session=session, url=station_url)

        parser = parsers.AirQualityParser(data)

        for station in parser.stations:
            LOGGER.info("Station ID: %s", station.id)

            site = build_site(station)
            site.save()

            sensor = build_sensor(station)
            sensor.save()


if __name__ == '__main__':
    main()

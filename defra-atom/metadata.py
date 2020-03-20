"""
Utilities to generate meta-data configuration files.
"""

import logging
import argparse
import pathlib

import settings
import parsers.inspire
import assets
import http_session

LOGGER = logging.getLogger(__name__)


def build_site(station: parsers.inspire.Station) -> assets.Site:
    """
    Map an Air quality monitoring Station to an Urban Flows Site

    https://uk-air.defra.gov.uk/data/so/stations/
    """

    site_id = station.id

    site = assets.Site(
        site_id=site_id,
        latitude=station.coordinates[0],
        longitude=station.coordinates[1],
        altitude=station.altitude['value'],
        address=None,
        city=station.name,
        country='United Kingdom',
        postcode=None,
        first_date=station.start_time.date(),
        operator=dict(
            email='aqevidence@defra.gsi.gov.uk',
            contact='https://www.gov.uk/government/organisations/department-for-environment-food-rural-affairs',
            address='Atmosphere and Noise, Resource Atmosphere and Sustainability, '
                    'Area 2C Nobel House, 17 Smith Square, London, SW1P 2AL',
        ),
        desc_url=station.info,
    )

    return site


def build_sensor(station: parsers.inspire.Station, sampling_point: parsers.inspire.SamplingPoint) -> assets.Sensor:
    """
    Map a Station and its Sampling Points to an Urban Flows Sensor (pod)

    Sampling point: An instrument or other device configured to measure an air quality
    https://uk-air.defra.gov.uk/data/so/sampling-points/
    """

    observed_property_url = sampling_point.observed_property
    unit_of_measurement_url = sampling_point.unit_of_measurement

    try:
        measure = settings.UNIT_MAP[unit_of_measurement_url][observed_property_url]
    except KeyError:
        LOGGER.error("%s: No unit metadata", sampling_point.id)
        return

    unit_of_measurement = measure['unit']
    label = measure['label']

    sensor = assets.Sensor(
        sensor_id=sampling_point.id,
        family='DEFRA_UK-AIR',
        provider=dict(
            id=sampling_point.belongs_to,
        ),
        detectors=[
            dict(
                name=label,
                unit=unit_of_measurement,
            ),
        ],
        desc_url=sampling_point.url,
        first_date=sampling_point.start_time.date().isoformat(),
    )

    return sensor


def get_data(input_path) -> iter:
    """Iterate over all raw data files"""
    for path in pathlib.Path(input_path).glob('**/*.xml'):
        LOGGER.info(path)

        # Parse XML document
        with open(path) as file:
            yield file.read()


def get_objects(feed, session):
    # Store objects to memory (don't re-fetch them every time they're encountered)
    stations = dict()
    sampling_points = dict()
    pairs = dict()

    for data in feed:
        parser = parsers.inspire.AirQualityParser(data)

        # Iterate over observations
        for observation in parser.observations:
            LOGGER.info(observation.id)

            # Generate metadata

            # Station
            station_url = observation.station
            try:
                stations[station_url]

            # Get new stations
            except KeyError:
                station = parsers.inspire.Station.get(session, station_url)
                stations[station_url] = station

                LOGGER.info("Station: %s", station.id)

            # Sampling point
            sampling_point_url = observation.sampling_point
            try:
                sampling_points[sampling_point_url]

            # Get new sampling points
            except KeyError:
                sampling_point = parsers.inspire.SamplingPoint.get(session, sampling_point_url)
                sampling_point.unit_of_measurement = observation.unit_of_measurement
                sampling_points[sampling_point_url] = sampling_point

                LOGGER.info("Sampling point: %s", sampling_point.id)

            # Build pairs
            pairs.setdefault(station_url, {sampling_point_url}).add(sampling_point_url)

    return stations, sampling_points, pairs


def configure_arguments():
    """Command-line arguments"""

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input', default=settings.DEFAULT_RAW_DIR, type=str, help="Input file directory")
    parser.add_argument('-v', '--verbose', action='store_true', help="Debug logging mode")

    return parser.parse_args()


def main():
    args = configure_arguments()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    session = http_session.DEFRASession()

    # Get DEFRA metadata objects from downloaded data
    feed = get_data(args.input)
    stations, sampling_points, pairs = get_objects(feed, session)

    # Iterate over objects and output metadata
    for station_url, sampling_point_urls in pairs.items():
        station = stations[station_url]

        for sampling_point_url in sampling_point_urls:
            sampling_point = sampling_points[sampling_point_url]

            # Map to Urban Flows
            site = build_site(station)
            sensor = build_sensor(station, sampling_point)

            # Serialise
            site.save()
            sensor.save()


if __name__ == '__main__':
    main()

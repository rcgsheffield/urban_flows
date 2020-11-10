"""
Translate from Aeroqual objects to Urban Flows Observatory metadata assets.
"""

import assets
import settings

from collections import Mapping, Iterable


def instrument_to_site(instrument: Mapping) -> assets.Site:
    """
    Map an Aeroqual instrument to an Urban Flows site (location) asset.
    """
    return assets.Site(
        site_id=instrument['serial'],
        operator=instrument['organisation'],
        desc_url=settings.DESC_URL,
    )


def sensor_to_detector(sensor: Mapping) -> dict:
    """
    Map an Aeroqual sensor to an Urban Flows detector (channel) asset.
    """

    return dict(
        name=settings.RENAME_COLUMNS[sensor['name']],
        # Fix encoding error that occurs on Windows
        unit=sensor['units'].replace('\xb3', '3'),
        # Nominal instrument error (10^-NDP)
        epsilon=10 ** (-sensor['decimalPlaces']),
    )


def instrument_to_sensor(instrument: Mapping) -> assets.Sensor:
    """
    Map an Aeroqual instrument to an Urban Flows sensor asset.
    """

    detectors = list()
    for s in instrument['sensors']:
        detectors.append(sensor_to_detector(s))

    return assets.Sensor(
        sensor_id=instrument['serial'],
        serial_number=instrument['serial'],
        family=settings.FAMILY,
        detectors=detectors,
    )

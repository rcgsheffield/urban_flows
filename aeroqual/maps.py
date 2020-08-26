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
        unit=sensor['units'],
        epsilon=sensor['decimalPlaces'],
    )


def instrument_to_sensor(instrument: Mapping) -> assets.Sensor:
    """
    Map an Aeroqual instrument to an Urban Flows sensor asset.
    """

    detectors = list()
    for s in instrument['sensors']:
        try:
            detectors.append(sensor_to_detector(s))
        except KeyError:
            if s['name'] in settings.IGNORE_METRICS:
                continue
            else:
                raise

    return assets.Sensor(
        sensor_id=instrument['serial'],
        family=settings.FAMILY,
        detectors=detectors,
    )

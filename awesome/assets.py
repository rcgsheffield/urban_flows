"""
Urban Flows Observatory assets
"""

import itertools
import logging
import requests

from settings import URL

LOGGER = logging.getLogger(__name__)


class Asset:
    """
    Urban Flows Observatory Asset
    """

    def __init__(self, identifier: str):
        """
        :param identifier: Unique identifier for this object
        """
        super().__init__()
        self.identifier = identifier


class Site(Asset):
    """
    Urban Flows Observatory site (geographical location)
    """
    pass


class Family(Asset):
    """
    Urban Flows Observatory family (type or group) of sensors
    """
    pass


class Sensor(Asset):
    """
    Urban Flows Observatory sensor
    """

    @classmethod
    def get_detectors_from_sensors(cls, sensors: dict) -> dict:
        """
        Get a mapping of all detectors on all sensors
        Each sensor pod contains multiple detectors (quantitative measurement
        channels). Different sensors may have detectors (channels) with the
        same name (but different properties perhaps)
        """
        # The key is the metric title e.g. 'MET_RH' or 'AQ_PM1'
        return {det['o'].upper(): det for det in
                itertools.chain(*(sensor['detectors'].values()
                                  for sensor_id, sensor in sensors.items()))}


def validate(metadata: dict):
    for site_id, site in metadata['sites'].items():
        assert site_id == site['name']
        assert isinstance(site['activity'], list)
        assert len(site['activity']) > 0


def get_metadata() -> dict:
    """
    Retrieve the metadata for Urban Flows Observatory assets. Download metadata
    from the portal and parse the document.

    The returned document has the following keys:
    dict_keys(['sites', 'families', 'pairs', 'sensors'])
    """
    with requests.Session() as session:
        response = session.get(URL, params=dict(aktion='json_META'))
        response.raise_for_status()
        metadata = response.json()

    validate(metadata)

    return metadata

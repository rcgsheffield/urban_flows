"""
Urban Flows Observatory assets
"""

import itertools
import logging
import requests
import datetime
import shelve
import pathlib
from typing import Optional

import settings
from settings import URL

LOGGER = logging.getLogger(__name__)


class BookmarkMixin:
    """
    Serialise the latest timestamp successfully replicated from the data stream
    """
    database = None

    def __init__(self):
        self.identifier = str()

        if self.database is None:
            self.database = self.open_database()

    @classmethod
    def database_path(cls) -> pathlib.Path:
        return settings.BOOKMARK_PATH_PREFIX.joinpath(cls.__name__.casefold())

    @classmethod
    def open_database(cls, *args, **kwargs):
        # Ensure directory exists
        cls.database_path().parent.mkdir(parents=True, exist_ok=True)
        return shelve.open(str(cls.database_path()), *args, **kwargs)

    @property
    def latest_timestamp(self) -> Optional[datetime.datetime]:
        """
        Retrieve the latest stored timestamp for this object, or null if no
        timestamp was stored.
        """
        try:
            return self.database[self.identifier]
        # No entry for this item
        except KeyError:
            pass

    @latest_timestamp.setter
    def latest_timestamp(self, timestamp: datetime.datetime):
        """
        Store a timestamp value associated with this object
        """
        self.database[self.identifier] = timestamp


class Asset(BookmarkMixin):
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

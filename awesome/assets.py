"""
Urban Flows Observatory assets
"""

import logging
import requests
import datetime
import json
import pathlib

import arrow.parser

import settings

LOGGER = logging.getLogger(__name__)

METADATA_URL = 'http://ufdev.shef.ac.uk/uflobin/ufdexF1'


class BookmarkMixin:
    """
    Serialise the latest timestamp successfully replicated from the data stream.
    """
    BOOKMARK_PATH = None

    @classmethod
    def load_sensor_bookmarks(cls) -> dict:
        try:
            with cls.BOOKMARK_PATH.open() as file:
                return dict(json.load(file))
        except FileNotFoundError:
            return dict()

    @classmethod
    def save_sensor_bookmarks(cls, bookmarks: dict):
        with cls.BOOKMARK_PATH.open('w') as file:
            json.dump(bookmarks, file, indent=2)
            LOGGER.debug("Wrote '%s'", file.name)

    @property
    def _latest_timestamp(self) -> str:
        try:
            return self.load_sensor_bookmarks()[self.name]
        # No entry exists
        except KeyError:
            return ''

    @property
    def latest_timestamp(self) -> datetime.datetime:
        timestamp = self._latest_timestamp
        try:
            return arrow.get(timestamp).datetime
        # Ignore empty strings
        except arrow.parser.ParserError:
            if timestamp:
                raise

    @latest_timestamp.setter
    def latest_timestamp(self, timestamp: datetime.datetime):
        bookmarks = self.load_sensor_bookmarks()
        if not timestamp:
            raise ValueError('No timestamp specified')
        bookmarks[self.name] = timestamp.isoformat()
        self.save_sensor_bookmarks(bookmarks)


class Asset(BookmarkMixin):
    """
    Urban Flows Observatory Asset
    """

    def __init__(self, name: str):
        self.name = name


class Sensor(Asset):
    """
    Urban Flows Observatory Sensor
    """
    BOOKMARK_PATH = pathlib.Path(settings.SENSOR_BOOKMARK_PATH)


class Site(Asset):
    """
    Urban Flows Observatory Site
    """
    BOOKMARK_PATH = pathlib.Path(settings.SITE_BOOKMARK_PATH)


def validate(metadata: dict):
    for site_id, site in metadata['sites'].items():
        assert site_id == site['name']
        assert isinstance(site['activity'], list)
        assert len(site['activity']) > 0


def _get_metadata() -> dict:
    """
    Retrieve the metadata for Urban Flows Observatory assets. Download metadata from the portal and parse the document.

    The returned document has the following keys: dict_keys(['sites', 'families', 'pairs', 'sensors'])
    """
    with requests.Session() as session:
        response = session.get(METADATA_URL, params=dict(aktion='json_META'))
        response.raise_for_status()
        metadata = response.json()

    validate(metadata)

    return metadata


def get_metadata() -> tuple:
    metadata = _get_metadata()

    pairs = list(metadata['pairs'].values())
    families = list(metadata['families'].values())
    sites = list(metadata['sites'].values())
    sensors = list(metadata['sensors'].values())

    return sites, families, pairs, sensors


if __name__ == '__main__':
    import logging
    import csv
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Print UFO metadata as CSV')
    parser.add_argument('--sites', action='store_true')
    parser.add_argument('--families', action='store_true')
    parser.add_argument('--pairs', action='store_true')
    parser.add_argument('--sensors', action='store_true')
    args = parser.parse_args()

    index = 0
    if args.families:
        index = 1
    elif args.pairs:
        index = 2
    elif args.sensors:
        index = 3

    logging.basicConfig(level=logging.INFO)

    writer = None
    rows = get_metadata()[index]
    for row in rows:
        if not writer:
            writer = csv.DictWriter(sys.stdout, fieldnames=row.keys())
            writer.writeheader()
        writer.writerow(row)

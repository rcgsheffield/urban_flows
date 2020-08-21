"""
Urban Flows Observatory assets
"""

import logging
import requests

LOGGER = logging.getLogger(__name__)

METADATA_URL = 'http://ufdev.shef.ac.uk/uflobin/ufdexF1'


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

    pairs = metadata['pairs'].values()
    families = metadata['families'].values()
    sites = metadata['sites'].values()
    sensors = metadata['sensors'].values()

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

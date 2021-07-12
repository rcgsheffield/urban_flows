"""
List UFO sites
"""

import logging
import sys
import csv
import json
import argparse

import assets

logger = logging.getLogger(__name__)


def get_args():
    """
    Command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    metadata = assets.get_metadata()
    sites = metadata['sites']

    logger.info('Retrieved %s sites', len(sites))

    # CSV output
    writer = None

    for site_id, site in sites.items():

        logger.debug(json.dumps(site))

        # Latest deployment
        activity = site['activity'][-1]
        row = dict(
            name=site['name'],
            latitude=site['latitude'],
            longitude=site['longitude'],
            activity_stAdd=activity['stAdd'],
            dbh=activity['dbh'],
        )

        if not writer:
            writer = csv.DictWriter(sys.stdout, fieldnames=row.keys(),
                                    lineterminator='\n')
            writer.writeheader()

        writer.writerow(row)

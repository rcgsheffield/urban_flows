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

if __name__ == '__main__':

    # Command line args
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    sites, families, pairs, sensors = assets.get_metadata()

    # CSV output
    writer = None

    for site in sites:

        logger.debug(json.dumps(site))

        # Latest deployment
        activity = site['activity'][-1]
        row = dict(
            name=site['name'],
            site=site['site'],
            latitude=site['latitude'],
            longitude=site['longitude'],
            activity_stAdd=activity['stAdd'],
            dbh=activity['dbh'],
        )

        if not writer:
            writer = csv.DictWriter(sys.stdout, fieldnames=row.keys(), lineterminator='\n')
            writer.writeheader()

        writer.writerow(row)

import logging
import sys
import csv
import json

import assets

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    sites, families, pairs, sensors = assets.get_metadata()

    # CSV output
    writer = csv.DictWriter(sys.stdout, fieldnames=['name', 'lat', 'lon', 'description', 'tags'], lineterminator='\n')
    writer.writeheader()

    for site in sites:
        logger.debug(json.dumps(site))

        # Latest deployment
        activity = site['activity'][-1]
        row = dict(
            name=site['name'],
            lat=site['latitude'],
            lon=site['longitude'],
            description=activity['stAdd'],
            tags=activity['dbh'],
        )
        writer.writerow(row)

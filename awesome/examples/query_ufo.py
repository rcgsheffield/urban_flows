import datetime
import logging
import argparse

import ufdex

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    # sites, families, pairs, sensors = assets.get_metadata()
    sensors = {'20926', '20927'}  # '24298', '2006150', '2009150'}

    now = datetime.datetime.now() - datetime.timedelta(days=1)

    for sensor in sensors:
        LOGGER.info("Sensor name: %s", sensor)

        query = dict(
            time_period=[
                now - datetime.timedelta(days=2),
                now,
            ],
            sensors={sensor},
        )
        query = ufdex.UrbanFlowsQuery(**query)

        # TODO sort chronologically
        for reading in query():
            if args.verbose:
                print(reading)

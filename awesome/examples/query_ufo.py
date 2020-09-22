import datetime
import logging

import ufdex
import assets

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # sites, families, pairs, sensors = assets.get_metadata()
    sensors = {'2006150', '2009150'}

    now = datetime.datetime.now()

    for sensor in sensors:
        LOGGER.info("Sensor name: %s", sensor)

        query = dict(
            time_period=[
                now - datetime.timedelta(minutes=300),
                now,
            ],
            sensors={sensor},
        )
        query = ufdex.UrbanFlowsQuery(**query)

        # TODO sort chronologically
        for row in query():
            print(row)

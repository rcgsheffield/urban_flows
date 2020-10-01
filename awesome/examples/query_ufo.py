import datetime
import logging

import ufdex

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # sites, families, pairs, sensors = assets.get_metadata()
    sensors = {'24298', '2006150', '2009150'}

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
        for row in query():
            print(row)

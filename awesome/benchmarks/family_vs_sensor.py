import logging
import datetime
import time
import sys

import ufdex
import assets

LOGGER = logging.getLogger(__name__)

START_TIME = datetime.datetime(2020, 1, 1)
TIME_PERIOD = (START_TIME, START_TIME + datetime.timedelta(days=31))

NUMBER = 1


def main():
    logging.basicConfig(level=logging.DEBUG)

    _, families, _, sensors = assets.get_metadata()

    start_time = time.time()
    # By family
    LOGGER.info(TIME_PERIOD)
    for family_name, family in families.items():
        query = ufdex.UrbanFlowsQuery(
            families={family_name},
            time_period=TIME_PERIOD
        )
        result = tuple(query())
        LOGGER.info("Family '%s' %s bytes", family_name,
                    sys.getsizeof(result))
    LOGGER.info('Partition by family: %s seconds', time.time() - start_time)

    # # By sensor
    # for sensor_name, sensor in sensors.items():
    #     query = ufdex.UrbanFlowsQuery(
    #         sensors={sensor_name},
    #         time_period=TIME_PERIOD
    #     )
    #     time_seconds = timeit.timeit('tuple(query())', globals=locals(),
    #                                  number=NUMBER)
    #     print(time_seconds)


if __name__ == '__main__':
    main()

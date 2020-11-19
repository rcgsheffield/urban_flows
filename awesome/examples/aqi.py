import logging
import datetime
import argparse

import aqi.operations

LOGGER = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    start = datetime.datetime(2020, 11, 1)
    end = start + datetime.timedelta(hours=24)

    # ('LD' + str(i).zfill(4) for i in range(1, 78))
    # ('S' + str(i).zfill(4) for i in range(1, 52))
    for site_id in {'S0002', 'S0003', 'LD0002', 'LD0072', 'S0002', '[SCC]1ACD2'}:
        data = aqi.operations.get_urban_flows_data(site_id=site_id, start=start, end=end)
        data = aqi.operations.calculate_air_quality(data)
        print(data.head())
        print('__________________')


if __name__ == '__main__':
    main()

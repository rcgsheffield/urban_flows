import logging

import aqi.operations

LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    for site_id in {'S0002', 'LD0072'}:
        data = aqi.operations.get_urban_flows_data(site_id=site_id)
        data = aqi.operations.calculate_air_quality(data)
        print(data.head())


if __name__ == '__main__':
    main()

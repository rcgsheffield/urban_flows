import logging
import datetime
import random
import itertools
import argparse
import pathlib

import aqi.operations

LOGGER = logging.getLogger(__name__)

DESCRIPTION = 'Export AQI readings to CSV'


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser.parse_args()


def build_csv_path(s: str) -> pathlib.Path:
    path = pathlib.Path.home().joinpath('aqi_csv')
    filename = "{}.csv".format(s).replace(':', '+')
    return path.joinpath(filename)


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    start = datetime.datetime(2020, 11, 1)
    end = start + datetime.timedelta(days=7)

    # Generate site IDS
    families = {'luftdaten', 'AMfixed', 'eWatch'}
    luftdaten = ('LD' + str(i).zfill(4) for i in range(1, 78))
    sites = ('S' + str(i).zfill(4) for i in range(1, 52))
    site_ids = list(itertools.chain(luftdaten, sites))
    random.shuffle(site_ids)

    for site_id in site_ids:
        data = aqi.operations.get_urban_flows_data(site_id=site_id, start=start, end=end)
        data = aqi.operations.calculate_air_quality(data)

        if data.empty:
            continue

        output_path = build_csv_path('_'.join((site_id, start.isoformat(), end.isoformat())))
        output_path.parent.mkdir(exist_ok=True, parents=True)
        data.to_csv(output_path)

        LOGGER.info("Wrote '%s'", output_path)


if __name__ == '__main__':
    main()

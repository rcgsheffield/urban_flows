import argparse
import logging
import datetime

import ufoizom.http_session
import ufoizom.utils
import ufoizom.settings

from ufoizom.objects import Device, Data

DESCRIPTION = """
This is a data pipeline to ingest sensor data from a collection of Environmental Monitoring Solutions (EMS)
AirSonde devices.
"""

USAGE = """
python . TODO
"""

LOGGER = logging.getLogger(__name__)


def parse_date(date: str) -> datetime.date:
    return datetime.datetime.strptime(date, ufoizom.settings.DATE_FORMAT).date()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(usage=USAGE, description=DESCRIPTION)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-c', '--config', help='Configuration file', default=ufoizom.settings.DEFAULT_CONFIG_FILE)
    parser.add_argument('-d', '--date', type=parse_date, required=True)
    return parser.parse_args()


def main():
    args = get_args()
    ufoizom.utils.configure_logging(args.verbose)
    session = ufoizom.utils.get_session(args.config)

    # Time parameters
    start = datetime.datetime.combine(args.date, datetime.time.min)
    end = datetime.datetime.combine(args.date + datetime.timedelta(days=1), datetime.time.min)
    average = datetime.timedelta(seconds=60)

    for device in Device.list(session):
        print(device)
        for data in Data.analytics(session, device['deviceId'], start, end, average):
            print(data)


if __name__ == '__main__':
    main()

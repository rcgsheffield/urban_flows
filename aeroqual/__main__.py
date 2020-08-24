import argparse
import datetime
import logging

import http_session
import settings
import utils
from objects import Instrument, Data

LOGGER = logging.getLogger(__name__)

DESCRIPTION = """
Aeroqual harvester for the Urban Flows Observatory.
"""


def date(day: str) -> datetime.datetime:
    return datetime.datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-g', '--debug', action='store_true')
    parser.add_argument('-e', '--error', help='Error log file path')
    parser.add_argument('-c', '--config', help='Config file', default=str(settings.DEFAULT_CONFIG_FILE))
    parser.add_argument('-d', '--date', help='Get data for this day (UTC)', type=date, required=True)
    parser.add_argument('-a', '--averagingperiod', help='period in minutes to average data – minimum 1 minute',
                        type=int, default=settings.DEFAULT_AVERAGING_PERIOD)
    parser.add_argument('-j', '--includejournal', action='store_true', help='Include journal entries')

    return parser.parse_args()


def get_data(session, serial: str, start: datetime.datetime, end: datetime.datetime, averagingperiod: int,
             includejournal: bool = False):
    """
    Fetch instrument data.

    serial = serial number of instrument
    start time = date/time of beginning of required data period (inclusive) – in instrument local time zone, format yyyy-mm-ddThh:mm:ss
    end time = date/time of end of required data period (not inclusive)
    averaging period = period in minutes to average data – minimum 1 minute
    include journal = (optional) whether to include journal entries – true or false
    """
    # from=2016-01-01T00:00:00&to=2016-01-02T00:00:00&averagingperiod=60&includejournal=false
    params = {
        'from': start.isoformat(),
        'to': end.isoformat(),
        'averagingperiod': averagingperiod,
        'includejournal': includejournal,
    }
    data = Data(serial)
    x = data.get(session, params=params)
    print(x)


def main():
    args = get_args()
    utils.configure_logging(verbose=args.verbose, debug=args.debug, error=args.error)

    session = http_session.AeroqualSession(config_file=args.config)

    LOGGER.debug(session)

    for serial_number in Instrument.list(session):
        LOGGER.info("Sensor serial number: %s", serial_number)

        inst = Instrument(serial_number)
        sensor = inst.get(session)

        start = args.date
        end = args.date + datetime.timedelta(days=1)
        body = get_data(session, serial_number, start=start, end=end, averagingperiod=args.averagingperiod,
                        includejournal=args.includejournal)
        print(body)


if __name__ == '__main__':
    main()

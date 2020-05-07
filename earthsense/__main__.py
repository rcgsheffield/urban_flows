"""
EarthSense Zephyr API interface

https://www.earthsense.co.uk/product-resources
"""

import os.path
import datetime
import logging
import configparser
import csv
import argparse

import http_session

LOGGER = logging.getLogger(__name__)

ISO_DATE = '%Y-%m-%d'
DESCRIPTION = """
Download EarthSense Zephyr data within a time range for all devices associated with a user account and write it to a
CSV file.
"""

DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser('~'), 'earthsense.cfg')


def parse_csv(lines: iter) -> iter:
    reader = csv.reader(lines)

    try:
        # Line 1 = headers (metric labels)
        headers = next(reader)

        # Line 2 = units of measurement
        units = next(reader)

    # No rows
    except StopIteration:
        return

    # Meta-data (units)
    meta = dict(zip(headers, units))
    meta = remove_empty_strings(meta)

    LOGGER.info(meta)

    yield from csv.DictReader(lines, fieldnames=headers)


def remove_empty_strings(row: dict) -> dict:
    return {key: value if value.strip() else None for key, value in row.items()}


def remove_nulls(row: dict) -> dict:
    return {key: None if value == 'None' else value for key, value in row.items()}


def clean(rows: iter, append: dict = None) -> iter:
    for row in rows:
        row.update(append)
        row = remove_nulls(row)

        del row['Timestamp-UTS']

        yield row


def get_data(session, start_time, end_time):
    for internal_device_id, device in session.devices.items():
        device_id = device['zNumber']

        LOGGER.info("Device info: %s", device)

        for slot in ('A', 'B'):
            LOGGER.info("Device %s slot %s", device_id, slot)

            lines = session.iter_data(device_id=device_id, slot=slot, start_time=start_time, end_time=end_time)
            rows = parse_csv(lines)
            rows = clean(rows, append=dict(device_id=device_id, slot=slot))

            yield from rows


def write_csv(path, rows):
    # Iterate over all slots on all devices
    with open(path, 'w', newline='') as file:
        writer = None

        for row in rows:

            if not writer:
                headers = tuple(row.keys())
                LOGGER.info("CSV headers: %s", headers)

                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()

            writer.writerow(row)

    LOGGER.info("Wrote '%s'", file.name)


def date(date_string: str) -> datetime.date:
    """Parse date"""
    return datetime.datetime.strptime(date_string, ISO_DATE).date()


def get_args():
    """Command-line arguments"""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION)
    parser.add_argument('-o', '--output', help="Output file path", required=True)
    parser.add_argument('-d', '--date', help="Date (UTC, ISO format)", type=date, required=True)
    parser.add_argument('-c', '--config', help="Config file", default=DEFAULT_CONFIG_PATH)
    parser.add_argument('-v', '--verbose', help="Debug logging level", action='store_true')
    args = parser.parse_args()

    return args


def get_credentials(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    return config['credentials']


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    credentials = get_credentials(args.config)
    session = http_session.ZephyrSession(username=credentials['username'], password=credentials['password'])

    # Build time range for specified day
    start_time = datetime.datetime.combine(date=args.date, time=datetime.time.min).replace(tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime.combine(date=args.date + datetime.timedelta(days=1), time=datetime.time.min).replace(
        tzinfo=datetime.timezone.utc)

    rows = get_data(session=session, start_time=start_time, end_time=end_time)
    write_csv(path=args.output, rows=rows)


if __name__ == '__main__':
    main()

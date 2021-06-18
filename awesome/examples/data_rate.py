"""
Estimate the number of readings produced by the Observatory
"""

import logging
import datetime
import requests
import csv

DATE = datetime.datetime(2021, 6, 1)

# http://ufdev.shef.ac.uk/uflobin/ufdexF1?Tfrom=2021-06-18T06:27:24&Tto=2021-06-18T09:27:24&aktion=CSV_show&freqInMin=5&tok=generic
URL = 'http://ufdev.shef.ac.uk/uflobin/ufdexF1'

LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    session = requests.Session()

    # Get families list
    response = session.get(URL, params=dict(aktion='json_META'))
    response.raise_for_status()
    metadata = response.json()
    families = set(metadata['families'].keys())

    # Total readings for all families
    total_row_count = 0
    total_reading_count = 0

    for family in families:
        LOGGER.info("Family '%s' date %s", family, DATE.date().isoformat())

        # Get all UFO Data
        response = session.get(URL, params=dict(
            Tfrom=DATE.isoformat(),
            tto=(DATE + datetime.timedelta(days=1)).isoformat(),
            aktion='CSV_show', tok='generic', freqInMin=5,
            byFamily=family,
        ))
        response.raise_for_status()

        lines = response.text.splitlines()

        # Remove empty lines, html and comments
        lines = (s for s in lines
                 if
                 s.strip() and not s.startswith('<') and not s.startswith('#'))

        # Parse CSV
        reader = csv.reader(lines)

        # Count readings
        reading_count = 0

        row_count = 0

        for row in reader:
            row_count += 1
            readings_in_this_row = len(row) - 2
            if readings_in_this_row < 1:
                raise ValueError(row)
            reading_count += readings_in_this_row

        print(row_count, 'rows')
        print(reading_count, 'readings')

        total_row_count += row_count
        total_reading_count += reading_count

    print(total_row_count, 'total rows for all families')
    print(total_reading_count, 'total readings for all families')


if __name__ == '__main__':
    main()

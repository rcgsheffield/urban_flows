"""
Utility functions (or examples) for working with the Awesome portal API
"""

import datetime

from objects import Location, ReadingCategory


def print_locations(session):
    for location in Location.list(session):
        print(location)


def print_location_readings(session, location_id: int):
    loc = Location(location_id)

    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime(2020, 1, 1)
    interval = datetime.timedelta(minutes=60)

    for reading in loc.readings(session, start, end, interval):
        print(reading)


def print_reading_categories(session):
    for cat in ReadingCategory.list(session):
        print(cat)

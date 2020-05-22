"""
Utility functions (or examples) for working with the Awesome portal API
"""

import datetime

from ufportal.objects import Location


def print_locations(session):
    for location in Location.list(session):
        print(location)


def add_location(session):
    data = {
        "name": "My location",
        "lat": 52.505897,
        "lon": -1.300277,
        "elevation": 100
    }

    print(Location.store(session, obj=data))


def print_location_readings(session, location_id: int):
    loc = Location(location_id)

    start = datetime.datetime(2020, 1, 1)
    end = datetime.datetime(2020, 1, 1)
    interval = datetime.timedelta(minutes=60)

    for reading in loc.readings(session, start, end, interval):
        print(reading)


def build_location_index(session) -> iter:
    """
    Map key-value pairs to map location name to location identifier

    Usage: locations = dict(ufportal.awesome_utils.build_location_index(session))
    """
    for loc in Location.list(session):
        yield loc['name'], loc['id']

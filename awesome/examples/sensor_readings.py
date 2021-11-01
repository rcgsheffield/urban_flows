"""
This script will get some recent sensor readings
"""

import logging
import random
from pprint import pprint
from getpass import getpass

import objects
import http_session

SENSOR_COUNT = 827

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # Connect to portal API
    session = http_session.PortalSession(token=getpass())

    # Get a random sensor (this might not work)
    sensor_id = random.choice(list(range(SENSOR_COUNT)))

    # Show sensor metadata
    sensor = objects.Sensor(sensor_id)
    print(repr(sensor))

    # Get recent data
    pprint(sensor.latest_reading(session))

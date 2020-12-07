import logging
import random
from pprint import pprint

import objects
import http_session

logging.basicConfig(level=logging.DEBUG)

session = http_session.PortalSession()

sensor_id = random.choice(list(range(827)))

sensor = objects.Sensor(sensor_id)
print(repr(sensor))

pprint(sensor.latest_reading(session))

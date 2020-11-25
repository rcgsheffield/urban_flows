import logging
import random
from pprint import pprint

import objects
import http_session

logging.basicConfig(level=logging.INFO)

session = http_session.PortalSession()

sensors = list(objects.Sensor.list_iter(session))

sensor_id = random.choice(sensors)['id']

sensor = objects.Sensor(sensor_id)
print(repr(sensor))

data = sensor.readings_iter(session)

for x in data:
    pprint(x)

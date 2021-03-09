import logging
import getpass
import datetime

import http_session
import objects

LOCATION_ID = 1472
SENSOR_ID = 1344

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    session = http_session.PortalSession(token=getpass.getpass('Enter token: '))

    location = objects.Location(LOCATION_ID)
    location_data = location.get(session)
    print(location_data)

    response = location.readings(session, from_=datetime.datetime.min, to=datetime.datetime.utcnow(),
                                 interval=datetime.timedelta(minutes=5))
    print(response.json())

    sensor = objects.Sensor(SENSOR_ID)
    sensor_data = sensor.get(session)
    print(sensor_data)

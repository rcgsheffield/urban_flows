import logging
import http_session
import objects
import settings

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    with settings.DEFAULT_TOKEN_PATH.open() as file:
        token = file.readline().rstrip('\n')

    session = http_session.PortalSession(token=token)
    # https://portal.urbanflows.ac.uk/api/sensor-types/2
    sensor_type = objects.SensorType(2)

    new_data = {'id': 2, 'name': 'LUFTDATEN', 'manufacturer': 'luftdaten', 'rating': 0}
    sensor_type.update(session, new_data)

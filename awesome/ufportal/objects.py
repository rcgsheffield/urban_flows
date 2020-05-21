import urllib.parse
import datetime


class Object:
    BASE_URL = 'https://ufportal.clients.builtonawesomeness.co.uk/api/'
    edge = None

    def __init__(self, identifier):
        self.identifier = identifier

    @classmethod
    def build_url(cls, *args, **kwargs) -> str:
        return urllib.parse.urljoin(cls.BASE_URL, *args, **kwargs)

    def urljoin(self, *args, **kwargs):
        return urllib.parse.urljoin(self.url, *args, **kwargs)

    @property
    def url(self):
        return self.build_url(self.build_endpoint(self.identifier))

    @classmethod
    def list(cls, session):
        url = cls.build_url(cls.edge)
        yield from session.get_iter(url=url)

    @classmethod
    def build_endpoint(cls, identifier) -> str:
        return '{}/{}'.format(cls.edge, identifier)

    @classmethod
    def show(cls, session, identifier):
        url = cls.build_url(cls.build_endpoint(identifier))
        return session.get(url)

    def get(self, session):
        return self.show(session, self.identifier)

    @classmethod
    def store(cls, session, **json):
        url = cls.build_url(cls.edge)
        # TODO fix this error 500
        return session.post(url, json=json)

    @classmethod
    def update(cls, session, **kwargs):
        url = cls.build_url(cls.edge)
        return session.patch(url, **kwargs)

    def delete(self, session):
        return session.delete(self.url)


class Location(Object):
    """A location represents a collection on sensors at set of co-ordinates."""
    edge = 'locations/'

    def readings(self, session, start: datetime.datetime, end: datetime.datetime, interval: datetime.timedelta):
        url = self.urljoin('readings')
        params = {
            'to': start.isoformat(),
            'from': end.isoformat(),
            'interval': Reading.interval(interval)
        }
        return session.get_iter(url, params=params)

    def readings_by_sensor(self, *args, **kwargs):
        return self.readings(*args, *kwargs)

    def sensors(self, session):
        url = self.urljoin('sensors')
        return session.get(url)

    @classmethod
    def update(cls, session, name, **kwargs):
        return super().update(session=session, json=dict(name=name), **kwargs)


class Reading(Object):
    """A reading represents a measurement taken by a Sensor/Device at a point in time."""

    @staticmethod
    def interval(interval: datetime.timedelta) -> str:
        """Convert time difference into a portal time interval"""
        minutes = int(interval.total_seconds() / 60)
        return '{}m'.format(minutes)


class Sensor(Object):
    """A Sensor represents a device which takes measurements/readings"""

    def add_sensor_category(self, session, sensor_category_id: int):
        """Add a Sensor to a Sensor Category"""
        url = self.urljoin('add-sensor-category')
        return session.post(url, json=dict(sensor_category_id=sensor_category_id))

    def remove_sensor_category(self, session, sensor_category_id: int):
        """Remove a Sensor from a Sensor Category"""
        url = self.urljoin('remove-sensor-category')
        return session.post(url, json=dict(sensor_category_id=sensor_category_id))


class SensorType(Object):
    """A Sensor Type represents a type of device. This could be based on model number, brand etc."""
    pass

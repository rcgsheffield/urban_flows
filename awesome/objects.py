import logging
import urllib.parse
import datetime
import json
import abc

import settings

LOGGER = logging.getLogger(__name__)


class AwesomeObject(abc.ABC):
    """
    An object on the Awesome platform
    
    API documentation: https://ufapidocs.clients.builtonawesomeness.co.uk/
    """
    BASE_URL = settings.BASE_URL
    edge = None

    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.identifier)

    @classmethod
    def build_url(cls, *args, **kwargs) -> str:
        """Build a URL by appending extra items"""
        url = '/'.join([cls.edge, *map(str, args)])
        return urllib.parse.urljoin(base=cls.BASE_URL, url=url, **kwargs)

    def urljoin(self, *args, **kwargs):
        return urllib.parse.urljoin(self.url, *args, **kwargs)

    @property
    def url(self):
        return self.build_url(self.identifier)

    @classmethod
    def list(cls, session, **kwargs) -> list:
        url = cls.build_url()
        body = session.call(url=url, **kwargs)

        # Make sure this isn't a paginated response
        if 'links' in body:
            raise ValueError('Unexpected pagination metadata, use list_iter instead')

        return body['data']

    @classmethod
    def list_iter(cls, session, **kwargs) -> iter:
        url = cls.build_url()
        yield from session.get_iter(url=url, **kwargs)

    @classmethod
    def show(cls, session, identifier, **kwargs):
        url = cls.build_url(identifier)
        return session.call(url, **kwargs)

    def get(self, session):
        return self.show(session, self.identifier)

    @classmethod
    def store(cls, session, obj: dict, **kwargs) -> dict:

        LOGGER.debug("Storing %s: %s", cls.__name__, obj)

        url = cls.build_url()
        try:
            response = session.post(url, json=obj, **kwargs)
            return response.json()

        # This POST request redirects to the HTML home page, so just return empty
        except json.JSONDecodeError:
            return dict()

    def update(self, session, obj, **kwargs):
        return session.patch(self.url, json=obj, **kwargs)

    def delete(self, session, **kwargs):
        return session.delete(self.url, **kwargs)

    def load(self, session):
        """Retrieve object data and set attributes"""
        obj = self.get(session)
        for name, value in obj.items():
            setattr(self, name, value)

    @classmethod
    def add(cls, session, obj, **kwargs):
        """Create a new object in the database"""
        _obj = cls.new(**obj)
        return cls.store(session, _obj, **kwargs)

    @staticmethod
    def new(**kwargs) -> dict:
        """Create a new dictionary  to represent this object"""
        raise NotImplementedError


class Location(AwesomeObject):
    """A location represents a collection on sensors at set of co-ordinates."""
    edge = 'locations'

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
        return session.call(url)

    @staticmethod
    def new(name: str, lat: float, lon: float, elevation: int) -> dict:
        """Construct a new Location object"""
        return dict(
            name=name,
            lat=lat,
            lon=lon,
            elevation=elevation,
        )


class Sensor(AwesomeObject):
    """A Sensor represents a device which takes measurements/readings"""
    edge = 'sensors'

    def add_sensor_category(self, session, sensor_category_id: int):
        """Add a Sensor to a Sensor Category"""
        url = self.urljoin('add-sensor-category')
        return session.post(url, json=dict(sensor_category_id=sensor_category_id))

    def remove_sensor_category(self, session, sensor_category_id: int):
        """Remove a Sensor from a Sensor Category"""
        url = self.urljoin('remove-sensor-category')
        return session.post(url, json=dict(sensor_category_id=sensor_category_id))

    @staticmethod
    def new(name: str, location_id: int, sensor_type_id: int, active: bool):
        return dict(
            name=name,
            location_id=location_id,
            sensor_type_id=sensor_type_id,
            active=active,
        )


class ReadingCategory(AwesomeObject):
    """A Reading Category is a way of categorising Reading Types which will allow users to filter their results.
    E.g. Weather, Traffic."""
    edge = 'reading-categories'

    @staticmethod
    def new(name: str, icon_name: str):
        return dict(
            name=name,
            icon_name=icon_name,
        )


class ReadingType(AwesomeObject):
    """A Reading Type represent a type of measurement, E.g. CO2, NO,"""
    edge = 'reading-types'

    def add_reading_category(self, session, reading_category_id: int):
        """Add a Reading Type to a Reading Category"""
        url = self.urljoin('add-reading-category')
        return session.post(url, json=dict(reading_category_id=reading_category_id))

    def remove_reading_category(self, session, reading_category_id: int):
        """Remove a Reading Type from a Reading Category"""
        url = self.urljoin('remove-reading-category')
        return session.post(url, json=dict(reading_category_id=reading_category_id))

    @staticmethod
    def new(name: str, min_value: float, max_value: float, unit: str):
        return dict(
            name=name,
            min_value=min_value,
            max_value=max_value,
            unit=unit,
        )


class SensorType(AwesomeObject):
    """A Sensor Type represents a type of device. This could be based on model number, brand etc."""
    edge = 'sensor-types'

    @staticmethod
    def new(name: str, manufacturer: str, rating: int):
        return dict(
            name=name,
            manufacturer=manufacturer,
            rating=rating,
        )


class SensorCategory(AwesomeObject):
    edge = 'sensor-categories'

    @staticmethod
    def new(name: str, icon_name: str):
        return dict(
            name=name,
            icon_name=icon_name,
        )


class Reading(AwesomeObject):
    """A reading represents a measurement taken by a Sensor/Device at a point in time."""
    edge = 'readings'

    @staticmethod
    def interval(interval: datetime.timedelta) -> str:
        """Convert time difference into a portal time interval e.g. '5m'"""
        minutes = int(interval.total_seconds() / 60)
        return '{}m'.format(minutes)

    @classmethod
    def store_bulk(cls, session, readings):
        """Bulk Store up to 100 Readings"""
        url = cls.build_url('bulk')
        return session.post(url, json=dict(readings=readings))

    @classmethod
    def new(cls, value: float, created: str, reading_type_id: int, sensor_id: int) -> dict:
        return dict(
            value=value,
            created=created,
            reading_type_id=reading_type_id,
            sensor_id=sensor_id,
        )

    @classmethod
    def delete_bulk(cls, session, start: datetime.datetime, end: datetime.datetime, reading_type_id: int):
        url = cls.build_url('bulk/delete')
        body = {
            'from': start.isoformat(),
            'to': end.isoformat(),
            'reading_type_id': reading_type_id,
        }
        return session.post(url, json=body)

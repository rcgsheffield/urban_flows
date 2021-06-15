"""
Awesome Portal API objects
"""

import logging
import urllib.parse
import datetime
import json
import abc

from typing import List, Dict, Iterable

import requests

import settings
import exceptions
import utils

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
        self._data = dict()

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
        return self.build_url(self.identifier) + '/'

    @classmethod
    def list(cls, session, **kwargs) -> list:
        url = cls.build_url()
        body = session.call(url=url, **kwargs)

        # Make sure this isn't a paginated response
        if 'links' in body:
            raise ValueError(
                'Unexpected pagination metadata, use list_iter instead')

        return body['data']

    @classmethod
    def list_iter(cls, session, **kwargs) -> iter:
        url = cls.build_url()
        yield from session.get_iter(url=url, **kwargs)

    @classmethod
    def show(cls, session, identifier, **kwargs):
        url = cls.build_url(identifier)
        return session.call(url, **kwargs)

    def get(self, session) -> dict:
        """
        Retrieve object data
        """
        return self.show(session, self.identifier)['data']

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
        LOGGER.debug('Updating %s', self)
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
        LOGGER.info("Adding %s: %s", cls.__name__, obj)
        _obj = cls.new(**obj)
        return cls.store(session, _obj, **kwargs)

    @staticmethod
    def new(**kwargs) -> dict:
        """Create a new dictionary  to represent this object"""
        raise NotImplementedError


class Location(AwesomeObject):
    """
    A location represents a collection on sensors at set of co-ordinates.
    """
    edge = 'locations'

    def readings(self, session, from_: datetime.datetime,
                 to: datetime.datetime, interval: datetime.timedelta):
        url = self.urljoin('readings')
        params = {
            'from': Reading.strftime(from_),
            'to': Reading.strftime(to),
            'interval': Reading.interval(interval)
        }
        return session.query(url, params=params)

    def readings_by_sensor(self, *args, **kwargs):
        return self.readings(*args, *kwargs)

    def sensors(self, session):
        url = self.urljoin('sensors')
        return session.call(url)

    @staticmethod
    def new(name: str, lat: str, lon: str, elevation: float,
            description: str) -> dict:
        """
        Construct a new Location object
        """
        return dict(
            name=name,
            lat=lat,
            lon=lon,
            elevation=elevation,
            description=description,
        )

    def aqi_readings(self, session):
        """
        Get AQI readings at this location
        """
        # https://github.com/rcgsheffield/urban_flows/issues/14
        return session.call(self.urljoin('aqi-readings'))


class Sensor(AwesomeObject):
    """
    A Sensor typically represents a physical device or "pod" which takes measurements/readings for a number of metrics
    (social or natural phenomena). Usually this means multiple channels of quantitative, time-based data.
    """
    edge = 'sensors'

    def add_sensor_category(self, session, sensor_category_id: int):
        """Add a Sensor to a Sensor Category"""
        url = self.urljoin('add-sensor-category')
        return session.post(url,
                            json=dict(sensor_category_id=sensor_category_id))

    def remove_sensor_category(self, session, sensor_category_id: int):
        """Remove a Sensor from a Sensor Category"""
        url = self.urljoin('remove-sensor-category')
        return session.post(url,
                            json=dict(sensor_category_id=sensor_category_id))

    @staticmethod
    def new(name: str, location_id: int, sensor_type_id: int, active: bool):
        return dict(
            name=name,
            location_id=location_id,
            sensor_type_id=sensor_type_id,
            active=active,
        )

    def readings(self, session) -> dict:
        """
        Undocumented endpoint giving the latest reading for this sensor
        """
        return session.call(self.urljoin('readings'))

    def latest_reading(self, session) -> dict:
        try:
            return self.readings(session)['data'][0]
        except IndexError:
            # No readings found so return None
            pass

    def latest_timestamp(self, session) -> datetime.datetime:
        """
        Get the timestamp of the most recent reading for this sensor
        """
        latest_reading = self.latest_reading(session=session)
        try:
            return utils.parse_timestamp(latest_reading['created'])
        except TypeError:
            # If no readings exist for this sensor then return null
            if latest_reading is not None:
                raise


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
        LOGGER.info("Adding reading category id %s to %s", reading_category_id,
                    self)
        url = self.urljoin('add-reading-category')
        return session.post(url, json=dict(
            reading_category_id=int(reading_category_id)))

    def remove_reading_category(self, session, reading_category_id: int):
        """Remove a Reading Type from a Reading Category"""
        LOGGER.info("Removing reading category id %s from %s",
                    reading_category_id, self)
        url = self.urljoin('remove-reading-category')
        return session.post(url,
                            json=dict(reading_category_id=reading_category_id))

    @staticmethod
    def new(name: str, min_value: float, max_value: float, unit: str):
        return dict(
            name=name,
            min_value=min_value,
            max_value=max_value,
            unit=unit,
        )


class SensorType(AwesomeObject):
    """
    A Sensor Type represents a type, or "family", of physical device. This could be based on model number, brand etc. of
    the asset.
    """
    edge = 'sensor-types'

    @staticmethod
    def new(name: str, manufacturer: str, rating: float):
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
    """
    A reading represents a measurement taken by a Sensor/Device at a point in time.
    """
    edge = 'readings'

    @staticmethod
    def strftime(time: datetime.datetime) -> str:
        return time.strftime(settings.AWESOME_DATE_FORMAT)

    @staticmethod
    def interval(interval: datetime.timedelta) -> str:
        """
        Convert time difference into a portal time interval in string format e.g. '5m'
        """
        minutes = int(interval.total_seconds() / 60)
        return '{minutes}m'.format(minutes=minutes)

    @classmethod
    def store_bulk(cls, session, readings) -> dict:
        """
        Bulk Store up to 100 Readings
        """
        url = cls.build_url('bulk')
        try:
            return session.call(url, method='post',
                                json=dict(readings=readings))
        except requests.HTTPError:
            if not readings:
                raise exceptions.EmptyValueError
            else:
                raise

    @classmethod
    def new(cls, value: float, created: str, reading_type_id: int,
            sensor_id: int) -> dict:
        return dict(
            value=value,
            created=created,
            reading_type_id=reading_type_id,
            sensor_id=sensor_id,
        )

    @classmethod
    def delete_bulk(cls, session, from_: datetime.datetime,
                    to: datetime.datetime, reading_type_id: int):
        url = cls.build_url('bulk/delete')
        body = {
            'from': cls.strftime(from_),
            'to': cls.strftime(to),
            'reading_type_id': reading_type_id,
        }
        return session.post(url, json=body)

    def readings(self, session):
        url = self.urljoin('readings')
        return session.call(url)


class AQIStandard(AwesomeObject):
    """
    Air Quality Index Standard represents an implementation of an Air Quality Index e.g. EU, British.
    """
    edge = 'aqi-standards'

    class Colour:
        GREEN = 'green'
        AMBER = 'amber'
        RED = 'red'
        VIOLET = 'violet'

    @classmethod
    def new(cls, name: str, breakpoints: List[Dict], description: str = None):
        """

        :param name: Name of the Standard
        :param description: A brief description of the standard
        :param breakpoints: An of breakpoints consisting of key-value pairs. min, max, color
        """
        return dict(
            name=name,
            breakpoints=breakpoints,
            description=description or '',
        )


class AQIReading(AwesomeObject):
    """
    An AQI Reading represents an air quality index calculation for a given point in time relating to an AQI standard.
    """
    edge = 'aqi-readings'

    @classmethod
    def new(cls, location_id: int, created: str, value: int,
            aqi_standard_id: int):
        return dict(
            location_id=location_id,
            created=created,
            value=value,
            aqi_standard_id=aqi_standard_id,
        )

    @classmethod
    def store_bulk(cls, session, aqi_readings: Iterable[Dict]):
        """
         Bulk Store AQI Readings

        :param session: Awesome portal HTTP session
        :param aqi_readings: e.g. [dict(created="2016-01-01 00:00:00", value=8, aqi_standard_id=1), ...]
        :return:
        """
        url = cls.build_url('bulk')
        return session.call(url, method='post',
                            json=dict(aqi_readings=list(aqi_readings)))

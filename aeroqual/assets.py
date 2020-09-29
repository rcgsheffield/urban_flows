"""
Classes for generating configuration files for the Urban Flows Observatory Asset Manager
"""

import os.path
import datetime
import logging

LOGGER = logging.getLogger(__name__)


class Asset:
    """
    A physical asset registered to the Urban Flows Observatory
    """

    def __str__(self):
        """Build asset configuration file"""

        lines = list()

        lines.append('begin.asset')

        # Build key-value pairs
        lines.extend(("{}={}".format(key, value or '') for key, value in self))

        lines.append('end.asset')

        # Line break at end-of-file
        lines.append('')

        return '\n'.join(lines)

    def __iter__(self):
        """Generate key-value pairs for output to configuration files"""
        raise NotImplementedError

    @property
    def subdir(self) -> str:
        parts = ['assets', "{}s".format(self.__class__.__name__.casefold())]

        subdir = os.path.join(*parts)

        os.makedirs(subdir, exist_ok=True)

        return subdir

    @property
    def filename(self) -> str:
        return '{}.txt'.format(self.id)

    @property
    def path(self) -> str:
        """File path"""
        return os.path.join(self.subdir, self.filename)

    def save(self):
        """Serialise asset configuration file"""
        with open(self.path, 'w+') as file:
            file.write(str(self))

            LOGGER.info("Wrote '%s'", file.name)

    @staticmethod
    def concat_dict(d: dict) -> str:
        """
        Build a string with this format from a dictionary e.g.

        dict(id='xx'|contact='xx'|tel='xxx')

        becomes

        id:xx|contact:xx|tel:xxxyyyyzzz|email:xxx@yyy
        """
        try:
            return '|'.join("{}:{}".format(key, value) for key, value in d.items())
        except AttributeError:
            return str()


class Site(Asset):
    """Physical location"""

    def __init__(self, site_id, latitude: float, longitude: float, altitude: float = None, address=None, city=None,
                 country=None, postcode=None, first_date: datetime.date = None, operator: dict = None,
                 desc_url: str = None):
        """
        Sensor site (physical location) registered to the Urban Flows Observatory

        :param site_id: unique identifier
        :param latitude: deg
        :param longitude: deg
        :param altitude: height above sea-level in meters
        :param address: [optional]
        :param city: [optional]
        :param country: [optional]
        :param postcode: [optional]
        :param first_date: When the site was commissioned
        :param operator: Who maintains the site
        :param desc_url: Website for further information
        """

        self.id = site_id
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.address = address
        self.city = city
        self.country = country
        self.postcode = postcode
        self.first_date = first_date
        self._operator = operator
        self.desc_url = desc_url

    def __iter__(self):
        yield 'siteid', self.id
        yield 'longitude_[deg]', self.longitude
        yield 'latitude_[deg]', self.latitude
        yield 'height_above_sea_level_[m]', self.altitude
        yield 'address', self.address
        yield 'city', self.city
        yield 'country', self.country
        yield 'Postal_Code', self.postcode
        yield 'firstdate', self.first_date
        yield 'operator', self.operator
        yield 'desc-url', self.desc_url

    @property
    def operator(self) -> str:
        return self.concat_dict(self._operator)


class Sensor(Asset):
    """
    A sensor registered to the Urban Flows Observatory
    """

    def __init__(self, sensor_id, family, detectors: list, provider: dict = None, serial_number=None,
                 energy_supply=None, freq_maintenance=None, s_type=None, data_acquisition_interval=None,
                 first_date=None, datoz18_handle=None, desc_url=None):
        """
        Sensor usage example:

        sensor = Sensor(
            sensor_id='my_sensor_01',
            family='AirQualityGizmo 9000',
            detectors=[
                dict(name='xxx'|unit='xxx'|epsilon='xxx'),
                dict(name='xxx'|unit='xxx'|epsilon='xxx'),
                dict(name='xxx'|unit='xxx'|epsilon='xxx'),
            ]
        )
        
        Decimal places
        NDP     Epsilon
        1       0.1
        2       0.01
        3       0.001

        epsilon = 10**{-NDP}

        :param sensor_id: Unique identifier
        :param family: The group or category of device
        :param detectors: Measurement capabilities of the device
        :type detectors: list[dict]
        :param provider:
        :param serial_number:
        :param energy_supply:
        :param freq_maintenance:
        :param s_type:
        :param data_acquisition_interval:
        :param first_date: The sensor has been operational since this time
        :param datoz18_handle:
        :param desc_url:
        """

        self.id = sensor_id
        self._provider = provider
        self.serial_number = serial_number
        self.energy_supply = energy_supply
        self.freq_maintenance = freq_maintenance
        self.s_type = s_type
        self.family = family
        self.data_acquisition_interval = data_acquisition_interval
        self.first_date = first_date
        self.datoz18_handle = datoz18_handle
        self._detectors = detectors
        self.desc_url = desc_url

    def __iter__(self):
        yield 'sensorid', self.id
        yield 'provider', self.provider
        yield 'serialnumber', self.serial_number
        yield 'energysupply', self.energy_supply
        yield 'freqmaintenance', self.freq_maintenance
        yield 'sType', self.s_type
        yield 'family', self.family
        yield 'data-acquisition-interval[min]', self.data_acquisition_interval
        yield 'firstdate', self.first_date
        yield 'datoz18-handle', self.datoz18_handle
        yield from self.detectors
        yield 'desc-url', self.desc_url

    @property
    def detectors(self) -> iter:
        for detector in self._detectors:
            yield 'detector', self.concat_dict(detector)

    @property
    def provider(self):
        return self.concat_dict(self._provider)

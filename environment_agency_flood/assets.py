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
    DIR = 'assets'
    SUBDIR = ''

    def __str__(self):
        """Build asset configuration file"""

        lines = list()

        lines.append('begin.asset')

        # Build key-value pairs
        lines.extend(("{}={}".format(key, value if value else '') for key, value in self))

        lines.append('end.asset')

        # Line break at end-of-file
        lines.append('')

        return '\n'.join(lines)

    def __iter__(self):
        """Generate key-value pairs for output to configuration files"""
        raise NotImplementedError

    @property
    def path(self) -> str:
        """File path"""

        subdir = os.path.join(self.DIR, self.SUBDIR)
        os.makedirs(subdir, exist_ok=True)
        filename = '{}.txt'.format(self.id)
        return os.path.join(subdir, filename)

    def save(self):
        """Serialise asset configuration file"""
        with open(self.path, 'w+') as file:
            file.write(str(self))

            LOGGER.info("Wrote '%s'", file.name)

    @staticmethod
    def concat_dict(d: dict) -> str:
        """
        Build a string with this format:

        id:xx|contact:xx|tel:xxxyyyyzzz|email:xxx@yyy
        """
        try:
            return '|'.join("{}:{}".format(key, value) for key, value in d.items())
        except AttributeError:
            return str()


class Site(Asset):
    """Physical location"""

    def __init__(self, site_id, latitude: float, longitude: float, altitude: float, address, city, country, postcode,
                 first_date: datetime.date, operator: dict, desc_url: str):
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

    SUBDIR = 'sensors'

    def __init__(self, sensor_id, family, detectors: list, provider: dict = None, serial_number=None,
                 energy_supply=None, freq_maintenance=None, s_type=None, data_acquisition_interval=None,
                 first_date=None, datoz18_handle=None, desc_url=None, iot_import_ip=None, iot_import_port=None,
                 iot_import_token=None, iot_import_username=None, iot_import_password=None, iot_export_ip=None,
                 iot_export_port=None, iot_export_token=None, iot_export_username=None, iot_export_password=None):
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

        # Internet of Things

        # Import
        self.iot_import_ip = iot_import_ip
        self.iot_import_port = iot_import_port
        self.iot_import_token = iot_import_token
        self.iot_import_username = iot_import_username
        self.iot_import_password = iot_import_password

        # Export
        self.iot_export_ip = iot_export_ip
        self.iot_export_port = iot_export_port
        self.iot_export_token = iot_export_token
        self.iot_export_username = iot_export_username
        self.iot_export_password = iot_export_password

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

        # IoT
        yield 'iot-import-IP', self.iot_import_ip
        yield 'iot-import-port', self.iot_import_port
        yield 'iot-import-token', self.iot_import_token
        yield 'iot-import-usrname', self.iot_import_username
        yield 'iot-import-pwd', self.iot_import_password

        yield 'iot-export-IP', self.iot_export_ip
        yield 'iot-export-port', self.iot_export_port
        yield 'iot-export-token', self.iot_export_token
        yield 'iot-export-usrname', self.iot_export_username
        yield 'iot-export-pwd', self.iot_export_password

    @property
    def detectors(self) -> iter:
        for detector in self._detectors:
            yield 'detector', self.concat_dict(detector)

    @property
    def provider(self):
        return self.concat_dict(self._provider)

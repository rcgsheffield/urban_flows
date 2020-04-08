import logging
import io
import datetime
import xml.etree.ElementTree

from collections import OrderedDict

import arrow

LOGGER = logging.getLogger(__name__)


class OWSException(RuntimeError):
    """
    https://www.ogc.org/standards/owc
    """
    pass


class InvalidParameterValueError(OWSException):
    pass


class UnknownQueryError(OWSException):
    pass


class XMLParser:
    NAMESPACES = dict()
    XLINK = dict(
        href='{http://www.w3.org/1999/xlink}href',
        title='{http://www.w3.org/1999/xlink}title',
    )

    def __init__(self, data):
        try:
            # Parse XML data
            self.root = self.parse(data)

        # Initialise with existing XML element
        except TypeError:
            if not isinstance(data, xml.etree.ElementTree.Element):
                raise
            self.root = data

    def __iter__(self):
        yield from self.root

    def __getitem__(self, item):
        return self.root[item]

    @staticmethod
    def get_namespaces(data: str) -> dict:
        """Build namespace map"""

        buffer = io.StringIO(data)

        # Use unique keys due to duplicated mappings
        namespaces = dict()

        for event, elem in xml.etree.ElementTree.iterparse(buffer, events=['start-ns']):
            namespaces[elem[0]] = elem[1]

        return namespaces

    @staticmethod
    def parse(data: str) -> xml.etree.ElementTree.Element:
        root = xml.etree.ElementTree.fromstring(data)

        return root

    def find(self, path: str) -> xml.etree.ElementTree.Element:
        return self.root.find(path, namespaces=self.NAMESPACES)

    def findall(self, path: str) -> list:
        return self.root.findall(path, namespaces=self.NAMESPACES)

    def iterfind(self, match: str) -> iter:
        return self.root.iterfind(match, namespaces=self.NAMESPACES)


class AirQualityParser(XMLParser):
    """
    Feature collection

    https://www.eea.europa.eu/data-and-maps/data/aqereporting-8
    """
    NAMESPACES = dict(
        xlink="http://www.w3.org/1999/xlink",
        xsd="http://www.w3.org/2001/XMLSchema",
        om="http://www.opengis.net/om/2.0",
        gml="http://www.opengis.net/gml/3.2",
        swe="http://www.opengis.net/swe/2.0",
        sams="http://www.opengis.net/samplingSpatial/2.0",
        sam="http://www.opengis.net/sampling/2.0",
        gmd="http://www.isotc211.org/2005/gmd",
        gco="http://www.isotc211.org/2005/gco",
        aqd="http://dd.eionet.europa.eu/schemaset/id2011850eu-1.0",
        am="http://inspire.ec.europa.eu/schemas/am/3.0",
        base="http://inspire.ec.europa.eu/schemas/base/3.3",
        base2="http://inspire.ec.europa.eu/schemas/base2/1.0",
        ompr="http://inspire.ec.europa.eu/schemas/ompr/2.0",
        ef="http://inspire.ec.europa.eu/schemas/ef/3.0",
        gn="urn:x-inspire:specification:gmlas:GeographicalNames:3.0",
        ad="urn:x-inspire:specification:gmlas:Addresses:3.0",
        xsi="http://www.w3.org/2001/XMLSchema-instance",
        ows='http://www.opengis.net/ows/1.1',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raise_exception()

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self.id)

    @property
    def id(self):
        return self.root.attrib['{http://www.opengis.net/gml/3.2}id']

    @property
    def header(self):
        return self.find('aqd:AQD_ReportingHeader')

    @property
    def observations(self) -> iter:
        for elem in self.iterfind('gml:featureMember/om:OM_Observation'):
            yield Observation(elem)

    @property
    def stations(self):
        for elem in self.iterfind('gml:featureMember/aqd:AQD_Station'):
            yield Station(elem)

    @property
    def sampling_points(self):
        for elem in self.iterfind('gml:featureMember/aqd:AQD_SamplingPoint'):
            yield SamplingPoint(elem)

    def raise_exception(self):
        elem = self.find('ows:Exception')
        try:
            code = elem.attrib['exceptionCode']
        except AttributeError:
            if elem:
                raise
            else:
                return

        text = elem[0].text.strip()

        LOGGER.error("%s: %s", code, text)

        if code == 'InvalidParameterValue':
            raise InvalidParameterValueError(text)
        elif code == 'NoApplicableCode':
            raise UnknownQueryError(text)
        else:
            raise RuntimeError(code, text)


class Observation(AirQualityParser):
    """
    OGC  Observations and Measurements
    https://www.ogc.org/standards/om
    """

    NAMESPACES = dict(
        om="http://www.opengis.net/om/2.0",
        gml="http://www.opengis.net/gml/3.2",
        xlink="http://www.w3.org/1999/xlink",
        xsi="http://www.w3.org/2001/XMLSchema-instance",
        gco="http://www.isotc211.org/2005/gco",
        ows='http://www.opengis.net/ows/1.1',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._parameters = None
        self._observed_property = None

    @staticmethod
    def parse_timestamp(timestamp: str) -> datetime.datetime:
        a = arrow.get(timestamp)

        return a.datetime

    @property
    def _result(self):
        return self.find('om:result')

    @property
    def result(self):
        return ResultParser(self._result)

    @property
    def parameters(self) -> dict:
        if not self._parameters:
            names = self.findall('om:parameter/om:NamedValue/om:name')
            values = self.findall('om:parameter/om:NamedValue/om:value')

            # Get URLs
            name_urls = (elem.attrib[self.XLINK['href']] for elem in names)
            value_urls = (elem.attrib[self.XLINK['href']] for elem in values)

            # Build key-value pairs
            self._parameters = OrderedDict(zip(name_urls, value_urls))

        return self._parameters

    @property
    def station(self) -> str:
        """Station URL"""
        return self.parameters['http://dd.eionet.europa.eu/vocabulary/aq/processparameter/Station']

    @property
    def sampling_point(self) -> str:
        return self.parameters['http://dd.eionet.europa.eu/vocabulary/aq/processparameter/SamplingPoint']

    @property
    def feature_of_interest(self) -> str:
        elem = self.find('om:featureOfInterest')

        url = elem.attrib[self.XLINK['href']]

        return url

    @property
    def observed_property(self):
        if self._observed_property is None:
            self._observed_property = self.find('om:observedProperty').attrib[self.XLINK['href']]

        return self._observed_property


class ResultParser(XMLParser):
    NAMESPACES = dict(
        swe='http://www.opengis.net/swe/2.0',
        ows='http://www.opengis.net/ows/1.1',
    )

    @property
    def _element_count(self) -> xml.etree.ElementTree.Element:
        return self.find('swe:DataArray/swe:elementCount/swe:Count/swe:value')

    @property
    def element_count(self) -> int:
        """Number of data rows in the result array"""
        return int(self._element_count.text)

    @property
    def _text_encoding(self) -> xml.etree.ElementTree.Element:
        return self.find('swe:DataArray/swe:encoding/swe:TextEncoding')

    @property
    def text_encoding(self) -> dict:
        return self._text_encoding.attrib

    @property
    def values_text(self):
        return self.find('swe:DataArray/swe:values').text.strip()

    @property
    def _fields(self):
        return self.iterfind('swe:DataArray/swe:elementType/swe:DataRecord/swe:field')

    @property
    def fields(self) -> dict:
        """Column meta-data"""

        fields = self._fields

        meta = OrderedDict()

        for field in fields:
            name = field.attrib['name']
            meta[name] = dict(definition=None, unit_of_measurement=None)

            meta[name]['definition'] = field[0].attrib['definition']

            # Unit of Measurement
            try:
                unit_of_measurement = field[0][0]

            # Ignore missing units
            except IndexError:
                continue

            try:
                # field -> Quantity -> uom
                meta[name]['unit_of_measurement'] = unit_of_measurement.attrib[self.XLINK['href']]

            # Non-standard units
            except KeyError:
                meta[name]['unit_of_measurement'] = unit_of_measurement.attrib['code']

        return meta

    @property
    def unit_of_measurement(self) -> str:
        return self.fields['Value']['unit_of_measurement']

    def iter_values(self) -> iter:
        """
        :return: Rows of data
        :rtype: iter[dict]
        """

        # Get metadata
        expected_rows = self.element_count
        text_encoding = self.text_encoding
        data = self.values_text
        fields = self.fields

        headers = fields.keys()

        lines = data.split(text_encoding['blockSeparator'])

        n_rows = 0

        for line in lines:
            # Build key-value pairs for each row
            values = line.split(text_encoding['tokenSeparator'])
            row = OrderedDict(zip(headers, values))

            yield row

            n_rows += 1

        # Validate row count
        if n_rows != expected_rows:
            raise ValueError('Unexpected number of rows')

        LOGGER.info("Generated %s rows of data", n_rows)


class SpatialObject(AirQualityParser):
    """
    DEFRA Air Quality Spatial Object Register

    https://uk-air.defra.gov.uk/data/so/about/
    """

    BASE_URL = 'http://environment.data.gov.uk/air-quality/so/'

    @property
    def url(self) -> str:
        return self.BASE_URL + self.id

    @classmethod
    def get(cls, session, url, **kwargs) -> str:
        """Utility to retrieve the data for a spatial object over HTTP"""
        return session.get(url, params=dict(format='application/xml'), **kwargs).text

    @property
    def name(self) -> str:
        return self.find('ef:name').text

    @property
    def position(self) -> tuple:
        """
        :returns: longitude, latitude
        """
        elem = self.find('ef:geometry/gml:Point/gml:pos')

        return tuple(float(s) for s in elem.text.split())

    @property
    def coordinates(self) -> tuple:
        """
        ISO 6709 coordinates
        """
        return (
            *self.position,
            self.altitude['value'],
            'urn:ogc:def:crs:OGC::CRS84',
        )

    @property
    def _time_period(self):
        return self.find('ef:operationalActivityPeriod')[0][0][0]

    @property
    def time_period(self) -> tuple:
        """
        Operational time period

        :rtype: tuple[datetime.datetime]
        """
        return tuple((
            # If the cell is empty then that time is undefined e.g. the object remains operational today
            arrow.get(elem.text).datetime if elem.text else None
            for elem in self._time_period
        ))

    @property
    def altitude(self) -> dict:
        elem = self.find('aqd:altitude')
        return dict(
            unit_of_measurement=elem.attrib['uom'],
            value=float(elem.text),
        )

    @property
    def start_time(self) -> datetime.datetime:
        return self.time_period[0]

    @property
    def belongs_to(self) -> str:
        """Network URL"""
        return self.find('ef:belongsTo').attrib[self.XLINK['href']]


class Station(SpatialObject):
    """
    Air quality monitoring Station

    A facility with one or more sampling points measuring ambient air quality pollutant concentrations

    https://uk-air.defra.gov.uk/data/so/stations/
    """

    @property
    def info(self) -> str:
        return self.find('aqd:stationInfo').text.strip()


class SamplingPoint(SpatialObject):
    """
    Air quality monitoring Sampling Point

    An instrument or other device configured to measure an air quality

    https://uk-air.defra.gov.uk/data/so/sampling-points/
    """

    @property
    def observed_property(self) -> str:
        """Observed property URL"""
        elem = self.find('ef:observingCapability/ef:ObservingCapability/ef:observedProperty')
        return elem.attrib[self.XLINK['href']]

    @property
    def broader(self):
        return self.find('ef:broader').attrib[self.XLINK['href']]

    @property
    def observed_property(self):
        return self.find('ef:observingCapability/ef:ObservingCapability/ef:observedProperty').attrib[self.XLINK['href']]

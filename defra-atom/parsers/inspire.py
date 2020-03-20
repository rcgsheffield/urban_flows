"""
XML and ATOM feed parsers to scrape, navigate and extract data
"""

import datetime
import logging
import statistics
import xml.etree.ElementTree

import haversine

import parsers.xml
import parsers.atom
import parsers.exceptions

LOGGER = logging.getLogger(__name__)

LOCATION = (53.38297, -1.4659)
DISTANCE = 50
UNIT = haversine.Unit.KILOMETERS


class InspireAtomParser(parsers.atom.AtomParser):
    """
    ATOM parser with additional functionality for working with INSPIRE data and network service specifications.
    """

    NAMESPACE_MAP = dict(
        **parsers.atom.AtomParser.NAMESPACE_MAP,
        inspire_dls='http://inspire-geoportal.ec.europa.eu/schemas/inspire/atom/1.0/atom.xsd',
        ef='http://inspire.ec.europa.eu/schemas/ef/3.0',
        aqd='http://dd.eionet.europa.eu/schemaset/id2011850eu-1.0',
        gml='http://www.opengis.net/gml/3.2',
    )

    @property
    def spatial_data_sets(self) -> list:
        return [DataSet(entry.root) for entry in self.entries]

    def filter_data_sets_by_distance(self, point, distance, unit) -> list:
        data_sets = list()

        for data_set in self.spatial_data_sets:

            try:
                # Check distance
                if data_set.calculate_distance(point, unit) < distance:
                    data_sets.append(data_set)

            # No distance available
            except TypeError:
                continue

        return data_sets


class DataSet(parsers.atom.Entry, InspireAtomParser):
    """
    Spatial Data Set
    """

    @property
    def polygon(self) -> str:
        try:
            return self.find('georss:polygon').text.strip()
        except AttributeError:
            return str()

    @property
    def coordinates(self) -> tuple:
        """Polygon coordinates"""
        coordinates = self.polygon

        # Parse strings to floats
        floats = tuple((float(s) for s in coordinates.split()))

        # Form coordinate pairs
        step = 2
        lat = floats[::step]
        long = floats[1::step]

        return tuple(zip(lat, long))

    @property
    def mean_latitude(self) -> float:
        return statistics.mean((t[0] for t in self.coordinates))

    @property
    def mean_longitude(self) -> float:
        return statistics.mean((t[1] for t in self.coordinates))

    @property
    def position(self) -> tuple:
        """Average central position of this geographical area"""
        return self.mean_latitude, self.mean_longitude

    def calculate_distance(self, point: tuple, unit: haversine.Unit):
        """Haversine distance to another point"""
        try:
            return haversine.haversine(self.position, point, unit=unit)
        except ValueError:
            return


class AirQualityParser(parsers.xml.XMLParser):
    """
    European Air Quality Reporting data model

    http://dd.eionet.europa.eu/schemaset/id2011850eu-1.0
    """

    NAMESPACE_MAP = dict(
        gml='http://www.opengis.net/gml/3.2',
        om='http://www.opengis.net/om/2.0',
    )

    @property
    def feature_members(self) -> list:
        return self.findall('gml:featureMember')

    @property
    def _observations(self) -> list:
        return self.findall('gml:featureMember/om:OM_Observation')

    @property
    def observations(self) -> list:
        return [Observation(elem) for elem in self._observations]


class Observation(parsers.xml.XMLParser):
    NAMESPACE_MAP = dict(
        gml='http://www.opengis.net/gml/3.2',
        om='http://www.opengis.net/om/2.0',
        swe='http://www.opengis.net/swe/2.0',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._observed_property = None
        self._parameters = None

    @property
    def id(self):
        return self.root.attrib['{http://www.opengis.net/gml/3.2}id']

    @property
    def result(self) -> xml.etree.ElementTree.Element:
        """Result data array element"""
        # Some of the XML documents have a different structure for some reason
        return self.find('om:result/swe:DataArray') or self.find('om:result')

    @property
    def _text_encoding(self) -> xml.etree.ElementTree.Element:
        return self.find_within(self.result, 'swe:encoding/swe:TextEncoding')

    @property
    def text_encoding(self) -> dict:
        return self._text_encoding.attrib

    @property
    def values(self):
        return self.find_within(self.result, 'swe:values')

    @property
    def values_text(self) -> str:
        s = self.values.text or str()
        return s.strip()

    @property
    def _element_count(self) -> xml.etree.ElementTree.Element:
        return self.find_within(self.result, 'swe:elementCount/swe:Count/swe:value')

    @property
    def element_count(self) -> int:
        """Number of data rows in the result array"""
        return int(self._element_count.text)

    @property
    def observed_property(self):
        return self.find('om:observedProperty')

    @property
    def observed_property_url(self) -> str:
        if not self._observed_property:
            elem = self.observed_property
            try:
                self._observed_property = elem.attrib[self.XLINK_HREF]
            except KeyError as exc:
                raise parsers.exceptions.MissingAttributeError from exc

        return self._observed_property

    @property
    def _fields(self):
        return self.findall_within(self.result, 'swe:elementType/swe:DataRecord/swe:field')

    @property
    def fields(self) -> dict:
        """Column meta-data"""

        fields = self._fields

        meta = dict()

        for field in fields:
            name = field.attrib['name']
            meta[name] = dict(definition=None, unit_of_measurement=None)

            meta[name]['definition'] = field[0].attrib['definition']

            # Unit of Measurement
            try:
                # field -> Quantity -> uom
                meta[name]['unit_of_measurement'] = field[0][0].attrib[self.XLINK_HREF]
            except IndexError:
                pass

        return meta

    @property
    def unit_of_measurement(self) -> str:
        """Unit of measurement URL"""
        return self.fields['Value']['unit_of_measurement']

    @property
    def sampling_point(self) -> str:
        try:
            return self.parameters['http://dd.eionet.europa.eu/vocabulary/aq/processparameter/SamplingPoint']
        except KeyError as exc:
            raise parsers.exceptions.MissingParameterError from exc

    @property
    def parameters(self) -> dict:
        if not self._parameters:
            names = self.findall('om:parameter/om:NamedValue/om:name')
            values = self.findall('om:parameter/om:NamedValue/om:value')

            # Get URLs
            name_hrefs = (elem.attrib[self.XLINK_HREF] for elem in names)
            value_hrefs = (elem.attrib[self.XLINK_HREF] for elem in values)

            # Build key-value pairs
            self._parameters = dict(zip(name_hrefs, value_hrefs))

        return self._parameters

    @property
    def station(self) -> str:
        """Station URL"""
        return self.parameters['http://dd.eionet.europa.eu/vocabulary/aq/processparameter/Station']

    def iter_values(self) -> iter:
        """
        :return: Rows of data
        :rtype: iter[dict]
        """
        expected_rows = self.element_count

        text_encoding = self.text_encoding

        data = self.values_text

        fields = self.fields
        headers = fields.keys()

        lines = data.split(text_encoding['blockSeparator'])

        n_rows = 0
        for line in lines:

            # Skip empty lines
            if not line:
                continue

            # Build key-value pairs for each row
            values = line.split(text_encoding['tokenSeparator'])
            row = dict(zip(headers, values))

            # Append meta-data
            row['unit_of_measurement'] = fields['Value']['unit_of_measurement']
            row['observed_property'] = self.observed_property_url
            row['station'] = self.station
            row['sampling_point'] = self.sampling_point

            yield row

            n_rows += 1

        # Validate row count
        if n_rows != expected_rows:
            raise ValueError('Unexpected number of rows')


class SpatialObject(InspireAtomParser):
    """
    Defra's Air Quality Spatial Object Register

    https://uk-air.defra.gov.uk/data/so/about/
    """

    def __init__(self, *args, **kwargs):
        super(SpatialObject, self).__init__(*args, **kwargs)

        # Go two levels down
        self.root = self.root[0][0]

    @classmethod
    def get(cls, *args, **kwargs):
        """Download the XML version of this URL"""
        return super().get(*args, **kwargs, params=dict(format='application/xml'))

    @property
    def id(self):
        return self.root.attrib['{http://www.opengis.net/gml/3.2}id']

    @property
    def name(self) -> str:
        return self.find('ef:name').text

    @property
    def description(self) -> str:
        return self.find('gml:description').text

    @property
    def coordinates(self) -> tuple:
        text = self.find('ef:geometry/gml:Point/gml:pos').text

        return tuple(float(s) for s in text.split())

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
            datetime.datetime.fromisoformat(elem.text.replace('Z', '+00:00')) if elem.text else None
            for elem in self._time_period
        ))

    @property
    def start_time(self) -> datetime.datetime:
        return self.time_period[0]

    @property
    def belongs_to(self) -> str:
        """Network URL"""
        return self.find('ef:belongsTo').attrib[self.XLINK_HREF]


class Station(SpatialObject):
    """
    Air quality monitoring Stations

    A facility with one or more sampling points measuring ambient air quality pollutant concentrations

    https://uk-air.defra.gov.uk/data/so/stations/
    """

    @property
    def altitude(self) -> dict:
        elem = self.find('aqd:altitude')
        return dict(
            unit_of_measurement=elem.attrib['uom'],
            value=float(elem.text),
        )

    @property
    def info(self) -> str:
        return self.find('aqd:stationInfo').text.strip()


class SamplingPoint(SpatialObject):
    """
     Air quality monitoring Sampling Points

    An instrument or other device configured to measure an air quality

    https://uk-air.defra.gov.uk/data/so/sampling-points/
    """

    @property
    def observed_property(self) -> str:
        """Observed property URL"""
        elem = self.find('ef:observingCapability/ef:ObservingCapability/ef:observedProperty')
        return elem.attrib[self.XLINK_HREF]

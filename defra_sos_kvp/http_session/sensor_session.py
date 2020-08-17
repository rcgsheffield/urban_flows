import datetime
import json
import logging

import requests

import settings

LOGGER = logging.getLogger(__name__)


class Service:
    # European Air Quality e-Reporting data model
    AIR_QUALITY_DATA = 'AQD'
    SENSOR_OBSERVATION_SERVICE = 'SOS'


class SensorSession(requests.Session):
    """
    DEFRA UK-AIR Sensor Observation Service

    Key-Value Pair (KVP) encoding of requests via HTTP GET.

    https://uk-air.defra.gov.uk/data/about_sos

        The UK-AIR SOS is built on a 52°North SOS implementation which supports the OGC SOS versions 1.0.0, 2.0.0 and
        the European Air Quality e-Reporting data model (AQD version 1.0.0)
    """

    BASE_URL = 'https://uk-air.defra.gov.uk/sos-ukair/service/'
    SERVICE = Service.AIR_QUALITY_DATA
    VERSION = '1.0.0'

    def __init__(self):
        super().__init__()

        self.headers.update({'User-Agent': settings.USER_AGENT})
        self._bounding_box = None

    def request(self, *args, **kwargs):
        response = super().request(*args, **kwargs)

        # Raise HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError:
            LOGGER.error(response.text)
            raise

        return response

    def call(self, request: str, params: dict = None, **kwargs):

        if params is None:
            params = dict()

        params = dict(
            request=request,
            service=self.SERVICE,
            version=self.VERSION,
            **params
        )

        LOGGER.debug("Request parameters: %s", json.dumps(params))

        response = self.get(self.BASE_URL, params=params, **kwargs)

        return response.text

    @property
    def capabilities(self):
        return self.call('GetCapabilities')

    @property
    def data_availability(self):
        return self.call('GetDataAvailability')

    def get_observation(self, **kwargs):
        """
        Get observation data endpoint. This is an API interface available via an XML KVP binding.

        This endpoint provides access to observations from sensors and sensor systems selected by spatial, temporal
        and thematic filtering.

        See: 12-006_OGC_Sensor_Observation_Service_Interface_Standard.pdf

        Section 8.3 GetObservation Operation

        13.2.3 GetObservation KVP Binding
        http://www.opengis.net/spec/SOS/2.0/req/kvp-core/go-request

        See Example 32 on page 88.

        XML schema: http://schemas.opengis.net/sos/2.0/sosGetObservation.xsd
        """
        return self.call('GetObservation', **kwargs)

    def get_observation_by_date_and_feature(self, date: datetime.date, sampling_features: iter):
        # Comma-separated unordered list of one or more URL- encoded URIs pointing to specific features of interest of
        # observations stored by the service.
        feature_of_interest = ','.join(sampling_features)
        return self.get_observation_by_date(date=date, params={'featureOfInterest': feature_of_interest})

    def get_observation_between(self, start: datetime.datetime, end: datetime.datetime = None, params=None, **kwargs):
        """
        Get data with temporal filter

        Requirement 117

        http://www.opengis.net/spec/SOS/2.0/req/kvp-core/go-temporalFilter-encoding
        """

        params = params or dict()

        if not end:
            end = datetime.datetime.utcnow()

        period = (t.replace(minute=0, second=0, microsecond=0).isoformat() for t in (start, end))
        value_reference = 'om:phenomenonTime'
        params = dict(
            # https://en.wikipedia.org/wiki/ISO_8601#Time_intervals
            temporalFilter='{},{}/{}'.format(value_reference, *period),
            **params
        )

        return self.get_observation(params=params, **kwargs)

    def get_observation_by_date(self, date: datetime.date, **kwargs):
        """Retrieve data, filtered by calendar date"""
        start = datetime.datetime.combine(date=date, time=datetime.time.min).replace(tzinfo=datetime.timezone.utc)
        end = start + datetime.timedelta(days=1)

        return self.get_observation_between(
            start=start,
            end=end,
            **kwargs
        )

    @property
    def bounding_box(self) -> list:
        """GeoJSON bounding box"""
        if not self._bounding_box:
            with open(settings.BOUNDING_BOX) as file:
                geo_json_bbox = json.load(file)
                # Get the first item in the nested list
                self._bounding_box = geo_json_bbox[0]
        return self._bounding_box

    @property
    def bounding_box_corners(self) -> tuple:
        """The lower corner and upper corner of the bounding box. Decimal degrees."""
        lower_corner = self.bounding_box[0]
        upper_corner = self.bounding_box[2]
        return lower_corner, upper_corner

    def get_observation_spatial(self):
        """
        ***THERE IS A BUG IN THE SERVER SOFTWARE FOR THIS ENDPOINT***
        See: https://github.com/52North/SOS/issues/793
        See: docs/DEFRA UK-AIR SOS spatial filter issue.eml

        OGC SOS 12-006 Requirement 116 -- KVP encoding
        http://www.opengis.net/spec/SOS/2.0/req/kvp-core/go-bbox-encoding

        OGC 06-121r3 section 10.2.3 Bounding box KVP encoding

        A WGS 84 bounding box shall be KVP encoded in a corresponding parameter value list, with the ordered listed
        values for the quantities:

            LowerCorner longitude, in decimal degrees
            LowerCorner latitude, in decimal degrees
            UpperCorner longitude, in decimal degrees
            UpperCorner latitude, in decimal degrees
            crs URI = “urn:ogc:def:crs:OGC:1.3:CRS84” (optional)
        """

        LOGGER.warning("API bug: https://github.com/52North/SOS/issues/793")

        lower_corner, upper_corner = self.bounding_box_corners

        namespaces = ['xmlns(om,http://www.opengis.net/om/2.0)']
        value_reference = 'om:featureOfInterest/*/sams:shape'
        # OGC 12-006 Requirement 116
        spatial_filter = [str(x) for x in (value_reference, *lower_corner, *upper_corner)]
        params = dict(
            namespaces=','.join(namespaces),
            spatialFilter=','.join(spatial_filter),
        )

        return self.get_observation(params=params)

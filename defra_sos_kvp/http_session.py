import logging
import datetime
import json

import requests
import requests_cache

LOGGER = logging.getLogger(__name__)


class Service:
    # European Air Quality e-Reporting data model
    AIR_QUALITY_DATA = 'AQD'
    SENSOR_OBSERVATION_SERVICE = 'SOS'


class SensorSession(requests_cache.CachedSession):
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

        self.headers.update({'User-Agent': 'Urban Flows Observatory'})

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

        LOGGER.info("Request parameters: %s", json.dumps(params))

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
        Get observation data

        12-006_OGC_Sensor_Observation_Service_Interface_Standard.pdf
        13.2.3 GetObservation KVP Binding
        http://www.opengis.net/spec/SOS/2.0/req/kvp-core/go-request

        http://schemas.opengis.net/sos/2.0/sosGetObservation.xsd
        """
        return self.call('GetObservation', **kwargs)

    def get_observation_between(self, start: datetime.datetime, end: datetime.datetime = None):
        """
        Requirement 117

        http://www.opengis.net/spec/SOS/2.0/req/kvp-core/go-temporalFilter-encoding
        """

        if not end:
            end = datetime.datetime.utcnow()

        period = (t.replace(minute=0, second=0, microsecond=0).isoformat() for t in (start, end))
        value_reference = 'om:phenomenonTime'
        params = dict(
            # https://en.wikipedia.org/wiki/ISO_8601#Time_intervals
            temporalFilter='{},{}/{}'.format(value_reference, *period),
        )

        return self.get_observation(params=params)

    def get_observation_date(self, date: datetime.date):
        start = datetime.datetime.combine(date=date, time=datetime.time.min).replace(tzinfo=datetime.timezone.utc)
        end = start + datetime.timedelta(days=1)

        return self.get_observation_between(
            start=start,
            end=end,
        )

    def get_observation_spatial(self):
        """
        ***THERE IS A BUG IN THE SERVER SOFTWARE FOR THIS ENDPOINT***
        See: https://github.com/52North/SOS/issues/793

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

        # lat, long
        # 53.46, -1.68 (Bradfield)
        # 53.24, -1.24 (Bolsover)
        latitude = [53.24, 53.46]  # north
        longitude = [-1.68, -1.24]  # east

        namespaces = ['xmlns(om,http://www.opengis.net/om/2.0)']
        value_reference = 'om:featureOfInterest/*/sams:shape'
        spatial_filter = [str(x) for x in (value_reference, longitude[0], latitude[0], longitude[1], latitude[1])]
        params = dict(
            namespaces=','.join(namespaces),
            spatialFilter=','.join(spatial_filter),
        )

        return self.get_observation(params=params)

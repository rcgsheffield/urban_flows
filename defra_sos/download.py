from http_session import DEFRASOSSession
import csv
from utils import build_dir
# from utils import get_value
import logging
import http_session
import urllib.parse
import json
import datetime

LOGGER = logging.getLogger(__name__)


class DEFRASOSHarvestor(object):
    """A harvestor for DEFRA Sensor Observation Services (SOS) observations"""

    def __init__(self, date, distance: int, update_meta, output_meta, logger):
        """Initiate the properties"""

        self.date = date
        self.distance = distance
        self.update_meta = update_meta
        self.output_meta = output_meta
        build_dir(self.output_meta)

        self.logger = logger

        self.session = http_session.DEFRASOSSession()
        self.base_url = 'https://uk-air.defra.gov.uk/sos-ukair/api/v1/'

        # Station filters
        self.filter = dict(
            # Radius around a geographic point
            near=dict(
                center=dict(
                    type='Point',
                    coordinates=[53.379699, -1.469815],
                ),
                radius=self.distance,  # km
            )
        )

        # CSV output
        self.columns = [
            'timestamp',
            'measure',
            'value',
            'lat',
            'long',
            'station',
            'parameter_name',
            'unit',
        ]

    def get_stations(self) -> iter:
        """
        List stations

        https://uk-air.defra.gov.uk/sos-ukair/static/doc/api-doc/#stations
        """

        # Build query parameters as JSON
        params = {key: json.dumps(value) for key, value in self.filter.items()}

        for _station in self.session.call(self.base_url, 'stations', params=params):
            LOGGER.debug(json.dumps(_station))

            # Build station endpoint
            station_id = _station['properties']['id']
            endpoint = "stations/{station_id}".format(station_id=station_id)

            # Get detailed station info
            station = self.session.call(self.base_url, endpoint)

            LOGGER.debug(json.dumps(station))

            yield station

    def get_data(self, station: dict) -> iter:
        """Generate rows of data for the specified station"""

        for timeseries_id, _timeseries in station["properties"]["timeseries"].items():

            LOGGER.debug(json.dumps(_timeseries))

            endpoint = "timeseries/{}".format(timeseries_id)

            timeseries = self.session.call(self.base_url, endpoint)

            LOGGER.debug(json.dumps(timeseries))

            station_id = station["properties"]["id"]
            param_name = timeseries["parameters"]["feature"]["label"]
            unit = timeseries["uom"]

            params = dict(
                timespan="P1D/{}".format(self.date.strftime("%Y-%m-%d")),
            )
            data = self.session.call(self.base_url, endpoint + "/getData", params=params)

            # Iterate over data points
            for row in data["values"]:
                # Insert station info
                row['station'] = station_id

                # Insert measure info
                row['parameter_name'] = param_name
                row['unit'] = unit

                yield row

    def transform(self, row: dict) -> dict:
        """Clean a row of data"""

        return row

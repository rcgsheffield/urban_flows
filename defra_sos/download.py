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

    def __init__(self, date, distance, update_meta, output_meta, logger):
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
        self.filter= dict(
                near=dict(
                    center=dict(
                        type='Point',
                        coordinates=[53.379699,-1.469815],
                        radius=50
                    )
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
        for station in self.session.call(self.base_url, 'stations', json=self.filter):
            station_id = station['properties']['id']
            endpoint = "stations/{station_id}".format(station_id=station_id)

            yield self.session.call(self.base_url, endpoint)

    def get_data(self, stations) -> iter:
        """Generate rows of data for the specified stations"""

        timeseries = dict()

        for station in stations:

            print(json.dumps(station, indent=2))

            timeseries_id = list(station["properties"]["timeseries"].keys())[0]

            endpoint_ts = "timeseries/{}".format(timeseries_id)
            timeseries = self.session.call(self.base_url, endpoint_ts)
            coordinates = station["geometry"]["coordinates"]
            lat = coordinates[1]
            long = coordinates[0]
            station_id = station["properties"]["id"]
            param_name = timeseries["parameters"]["feature"]["label"]
            unit = timeseries["uom"]

            params = dict(
                timespan="P1D/{}".format(self.date.strftime("%Y-%m-%d")),
                limit=10000
            )
            data = self.session.call(self.base_url, endpoint_ts+"/getData", params=params)

            # Iterate over data points
            for row in data["values"]:

                # Insert station info
                row['lat'] = lat
                row['long'] = long
                row['station'] = station_id

                # Insert measure info
                row['parameter_name'] = param_name
                row['unit'] = unit

                yield row

    def transform(self, row: dict) -> dict:
        """Clean a row of data"""

        return row


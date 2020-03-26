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
        self.filters = urllib.parse.quote(
            """{"center":{"type":"Point","coordinates":[53.379699,-1.469815]},"radius":50}""")

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
        Get unique stations

        :type filters: iter[dict]
        """

        station_ids = set()

        for query in [self.filters]:
            data = self.session.call(self.base_url, 'stations?near={}'.format(query))

            for station in data[0:1]:
                station_id = station['properties']['id']

                # Skip repeated stations
                if station_id not in station_ids:
                    station_ids.add(station_id)

                    yield self.session.call(self.base_url, 'stations/{}'.format(station_id))

    def get_data(self, stations) -> iter:
        """Generate rows of data for the specified stations"""

        timeseries = dict()

        for station in stations:

            for key, value in station.items():
                self.logger.info("STATION %s: %s", key, value)

            timeseries_id = list(station["properties"]["timeseries"].keys())[0]

            endpoint_ts = "timeseries/{}".format(timeseries_id)
            timeseries = self.session.call_iter(self.base_url, endpoint_ts)
            timeseries = json.loads(list(timeseries)[0])

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
            ep2 = endpoint_ts+"/getData"
            data = self.session.call(self.base_url, endpoint_ts+"/getData", params=params)
            rows = data["values"]

            # Iterate over data points
            for row in rows:

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

        dt = row.pop('timestamp')
        row['timestamp'] = datetime.datetime.fromtimestamp(dt/1000)

        return row


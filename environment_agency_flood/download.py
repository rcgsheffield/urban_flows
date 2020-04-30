from http_session import FloodSession
import csv
from utils import make_dir
import logging
import http_session

LOGGER = logging.getLogger(__name__)

class FloodHarvestor(object):
    """A harvestor for Environment Agency Flood observations"""

    def __init__(self, date, distance, update_meta, output_meta, logger):
        """Initiate the properties"""

        self.date = date
        self.distance = distance
        self.update_meta = update_meta
        self.output_meta = output_meta
        make_dir(self.output_meta)

        self.logger = logger

        self.session = http_session.FloodSession()
        self.base_url = 'https://environment.data.gov.uk/flood-monitoring/'

        # Station filters
        self.coordinates = (53.379699, -1.469815)  # lat, long
        self.distance = 30  # km
        self.catchments = {
            'Derbyshire Derwent',
            'Idle and Torne',
            'Don and Rother',
            'Rother',
        }
        self.filters = [
            # Within distance from a point
            dict(
                lat=self.coordinates[0],
                long=self.coordinates[1],
                dist=self.distance,
            ),
            # Drainage basins
            *(dict(parameter='level', catchmentName=catchment) for catchment in self.catchments),
        ]

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

        for query in self.filters[1:2]:
            data = self.session.call(self.base_url, 'id/stations', params=query)

            for station in data['items'][1:2]:
                station_id = station['@id']

                # Skip repeated stations
                if station_id not in station_ids:
                    station_ids.add(station_id)

                    yield self.session.call(self.base_url, 'id/stations/{}'.format(
                        station['notation'])) if self.update_meta else station

    def get_data(self, stations) -> iter:
        """Generate rows of data for the specified stations"""

        measures = dict()

        for station in stations:

            for key, value in station.items():
                self.logger.info("STATION %s: %s", key, value)

            endpoint = 'id/stations/{station_id}/readings.csv'.format(
                station_id=station["items"]["stationReference"])

            params = dict(
                date=self.date.strftime("%Y-%m-%d"),
                _limit=10000
            )
            data = self.session.call_iter(self.base_url, endpoint, params=params)

            reader = csv.DictReader(data)

            # Iterate over data points
            for row in reader:

                # Insert station info
                row['lat'] = station["items"]["lat"]
                row['long'] = station["items"]["long"]
                row['station'] = station["items"]["@id"]

                # Get measure info
                try:
                    measure = measures[row['measure']]
                except KeyError:
                    # Get measure if not already retrieved
                    measure = self.session.get(row['measure']).json()['items']
                    # Save for re-use
                    measures[measure['@id']] = measure

                # Insert measure info
                row['parameter_name'] = measure['parameterName']
                row['unit'] = measure['unitName']

                yield row

    def transform(self, row: dict) -> dict:
        """Clean a row of data"""

        row['timestamp'] = row.pop('dateTime')

        return row


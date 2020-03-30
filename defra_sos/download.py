import logging
import json

import utils
import constants
import http_session

LOGGER = logging.getLogger(__name__)


class DEFRASOSHarvestor(object):
    """A harvestor for DEFRA Sensor Observation Services (SOS) observations"""

    def __init__(self, date, distance: int, update_meta, output_meta):
        """Initiate the properties"""

        self.date = date
        self.distance = distance
        self.update_meta = update_meta
        self.output_meta = output_meta

        utils.build_dir(self.output_meta)

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
            # Get detailed station info
            station_id = _station['properties']['id']
            endpoint = "stations/{station_id}".format(station_id=station_id)
            station = self.session.call(self.base_url, endpoint)

            yield station

    def get_data(self, station: dict) -> iter:
        """
        Generate rows of data for the specified station

        Time series getData endpoint:
        https://uk-air.defra.gov.uk/sos-ukair/static/doc/api-doc/#timeseries
        """

        for timeseries_id, timeseries in station["properties"]["timeseries"].items():

            station_id = station["properties"]["id"]
            observed_property = timeseries["phenomenon"]["label"]

            # Get data
            endpoint = 'timeseries/{timeseries_id}/getData'.format(timeseries_id=timeseries_id)

            params = dict(
                timespan="{duration}/{end}".format(
                    # One-day period
                    duration='P1D',
                    end=self.date.strftime(constants.DATE_FORMAT),
                ),
            )
            data = self.session.call(self.base_url, endpoint, params=params)

            rows = data['values']

            LOGGER.info("Station %s, time series %s: Retrieved %s rows", station_id, timeseries_id, len(rows))

            # Iterate over data points
            for row in rows:
                # Append metadata
                row['sensor'] = station_id
                row['observed_property'] = observed_property

                yield row

    def transform(self, row: dict) -> dict:
        """Clean a row of data"""

        return row

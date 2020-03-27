"""
Environment Agency real-time flood monitoring API

https://environment.data.gov.uk/flood-monitoring/doc/reference
"""

import logging
import urllib.parse
import requests
import datetime
import csv
import argparse
import json
import os

DESCRIPTION = """
Retrieve data from the Environment Agency real-time flood monitoring API and save it to file in CSV format.
"""

LOGGER = logging.getLogger(__name__)

class FloodSession(requests.Session):
    """
    Environment Agency real-time flood monitoring API HTTP session

    https://environment.data.gov.uk/flood-monitoring/doc/reference
    """

    def _call(self, base_url, endpoint, **kwargs) -> requests.Response:
        """Base request"""

        # Build URL
        url = urllib.parse.urljoin(base_url, endpoint)
        
        response = self.get(url, **kwargs)

        # HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            LOGGER.error(e)
            LOGGER.error(e.response.text)
            raise

        return response

    def call(self, base_url: str, endpoint: str, **kwargs) -> dict:
        """Call JSON endpoint"""

        response = self._call(base_url, endpoint, **kwargs)

        data = response.json()

        for meta, value in data['meta'].items():
            LOGGER.debug("META %s: %s", meta, value)

        return data

    def call_iter(self, base_url: str, endpoint: str, **kwargs) -> iter:
        """Generate lines of data"""

        response = self._call(base_url, endpoint, stream=True, **kwargs)

        yield from response.iter_lines(decode_unicode=True)

class FloodHarvestor(object):
    """A harvestor to get flood observations from Environment Agency"""
    
    def __init__(self, date, distance, update_meta, output_meta, logger):
        """Initiate the properties"""
        
        self.date = date
        self.distance = distance
        self.update_meta = update_meta
        self.output_meta = output_meta
        self.create_folder(self.output_meta)
        
        self.logger = logger
        
        self.session = FloodSession()
        self.base_url = 'https://environment.data.gov.uk/flood-monitoring/'

        # Station filters
        self.coordinates = (53.379699, -1.469815)  # lat, long
        self.distance  = 30  # km
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
            data = self.session.call(self.base_url,'id/stations', params=query)
            
            for station in data['items'][1:2]:                
                station_id = station['@id']                

                # Skip repeated stations
                if station_id not in station_ids:
                    station_ids.add(station_id)               
                    
                    yield self.session.call(self.base_url,'id/stations/{}'.format(station['notation'])) if self.update_meta else station

    def get_data(self) -> iter:
        """Generate rows of data for the specified stations"""

        measures = dict()
        
        stations = list(self.get_stations())

        for station in stations:

            for key, value in station.items():
                self.logger.info("STATION %s: %s", key, value)

            station_id = station['stationReference']
            endpoint = 'id/stations/{station_id}/readings.csv'.format(station_id=station_id)
            
            params = dict(
                date=self.date.strftime("%Y-%m-%d"),
                _limit=10000
            )
            data = self.session.call_iter(self.base_url,endpoint, params=params)
            
            reader = csv.DictReader(data)

            # Iterate over data points
            for row in reader:

                # Insert station info
                row['lat'] = station['lat']
                row['long'] = station['long']
                row['station'] = station['@id']

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

    def create_folder(self,path):
        if not os.path.exists(path):
            os.makedirs(path)

    def get_site_mapping(self, station):
        """Generate a metafile for a site"""
        
        result = dict()

        result["siteid"] =                       station['stationReference']
        result["longitude_[deg]"] =              station['lat']
        result["latitude_[deg]"] =               station['long']
        result["height_above_sea_level_[m]"] =   ""
        result["address"] =                      ", ".join((
                                                            station['label'],
                                                            station.get('eaAreaName', ''),
                                                            station.get('eaRegionName', ''),
        ))
        result["city"] =                         station['town']
        result["country"] =                      "United Kingdom"
        result["Postal_Code"] =                  ""
        result["firstdate"] =                    station['dateOpened']
        result["operator"] =                     ''
        result["desc-url"] =                     station['@id']

        return result
        
    def get_sensor_mapping(self, station):
        """Generate a metafile for a sensor"""
        
        sensors = list()
        measures = station['measures']
        measures = [measures] if type(measures) == dict else measures

        for i, measure in enumerate(measures):
            result = dict()

            result["sensorid"] =                     measure["@id"]
            result["provider"] =                     ''
            result["serialnumber"] =                 ""
            result["energysupply"] =                 "" 
            result["freqmaintenance"] =              "" 
            result["sType"] =                        measure['parameter']
            result["family"] =                       measure['parameterName']
            result["data-acquisition-interval[min]"] ="daily"
            result["firstdate"] =                    station['dateOpened']
            result["datoz18-handle"] =               ""
            result["detector"] =                     ""
            result["desc-url"] =                     "" 
            result["iot-import-IP"] =                "" 
            result["iot-import-port"] =              "" 
            result["iot-import-token"] =             "" 
            result["iot-import-usrname"] =           "" 
            result["iot-import-pwd"] =               "" 
            result["iot-export-IP"] =                "" 
            result["iot-export-port"] =              "" 
            result["iot-export-token"] =             "" 
            result["iot-import-usrname"] =           "" 
            result["iot-import-pwd"] =               ""

            sensors.append(result)    
        
        return sensors
        
    def generate_metadata(self, station):
        """Generate metadata for each station"""

        LOGGER.debug(json.dumps(station))
        
        # Site meta output to file
        self.create_folder("{}/sites".format(self.output_meta))
        site_file = "{}/sites/{}".format(self.output_meta, station['stationReference'])
        with open(site_file, 'w+') as file:
            file.write("begin.asset\n")
            for key, value in self.get_site_mapping(station).items():
                file.write('{k}={v}\n'.format(k=key, v=value))
            file.write("end.asset\n")

        # Sensor meta output to file
        self.create_folder("{}/sensors".format(self.output_meta))
        for sensor in self.get_sensor_mapping(station):
            sensor_file = "{}/sensors/{}".format(self.output_meta,sensor["sensorid"][60:])
            with open(sensor_file, 'w+') as file:
                file.write("begin.asset\n")
                for key,value in list(sensor.items()):
                    file.write('{k}={v}\n'.format(k=key,v=value))
                file.write("end.asset\n")


def get_args() -> argparse.Namespace:
    """Command-line arguments"""

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-d', '--date', required=True, type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), help="ISO UTC date")
    parser.add_argument('-od', '--output_data', required=True, type=str, help="Output CSV file path")
    parser.add_argument('-k', '--distance', type=int, help="Radius distance (km)", default=30)
    parser.add_argument('-um', '--update_meta', type=bool, help="True if update the metadata", default=False)
    parser.add_argument('-om', '--output_meta', type=str, help="Output folder path for metadata files")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable debug log mode")

    args = parser.parse_args()

    return args

def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    
    fh = FloodHarvestor(args.date, args.distance, args.update_meta, args.output_meta, LOGGER)
    
    # CSV output to file
    with open(args.output_data, 'w', newline='') as file:
        writer = csv.DictWriter(file, fh.columns)
        writer.writeheader()

        # Generate data
        for row in fh.get_data():
            row = fh.transform(row)
            writer.writerow(row)

if __name__ == '__main__':
    main()

"""
Run the test suite for download
"""

import logging
import unittest
import json
import metadata
import utils
import os

LOGGER = logging.getLogger(__name__)

class TestMetadata(unittest.TestCase):

    cls = metadata.DEFRASOSHarvestorMeta("meta")
    test = json.loads(
        """{"@context": "http://environment.data.gov.uk/flood-monitoring/meta/context.jsonld", "meta": {"publisher": "Environment Agency", "licence": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/", "documentation": "http://environment.data.gov.uk/flood-monitoring/doc/reference", "version": "0.9", "comment": "Status: Beta service", "hasFormat": ["http://environment.data.gov.uk/flood-monitoring/id/stations/4115.rdf", "http://environment.data.gov.uk/flood-monitoring/id/stations/4115.ttl", "http://environment.data.gov.uk/flood-monitoring/id/stations/4115.html"]}, "items": {"@id": "http://environment.data.gov.uk/flood-monitoring/id/stations/4115", "RLOIid": "2146", "catchmentName": "Idle and Torne", "dateOpened": "1992-05-01", "eaAreaName": "Midlands - Derbyshire Nottinghamshire and Leicestershire", "eaRegionName": "Midlands", "easting": 455970, "label": "Mansfield The Dykes", "lat": 53.166753, "long": -1.164236, "measures": {"@id": "http://environment.data.gov.uk/flood-monitoring/id/measures/4115-level-stage-i-15_min-mASD", "datumType": "http://environment.data.gov.uk/flood-monitoring/def/core/datumASD", "label": "Mansfield The Dykes LVL - level-stage-i-15_min-mASD", "latestReading": {"@id": "http://environment.data.gov.uk/flood-monitoring/data/readings/4115-level-stage-i-15_min-mASD/2020-03-22T18-00-00Z", "date": "2020-03-22", "dateTime": "2020-03-22T18:00:00Z", "measure": "http://environment.data.gov.uk/flood-monitoring/id/measures/4115-level-stage-i-15_min-mASD", "value": 0.308}, "notation": "4115-level-stage-i-15_min-mASD", "parameter": "level", "parameterName": "Water Level", "period": 900, "qualifier": "Stage", "station": "http://environment.data.gov.uk/flood-monitoring/id/stations/4115", "stationReference": "4115", "type": ["http://environment.data.gov.uk/flood-monitoring/def/core/Measure", "http://environment.data.gov.uk/flood-monitoring/def/core/WaterLevel"], "unit": "http://qudt.org/1.1/vocab/unit#Meter", "unitName": "mASD", "valueType": "instantaneous"}, "northing": 363620, "notation": "4115", "riverName": "River Maun", "stageScale": {"@id": "http://environment.data.gov.uk/flood-monitoring/id/stations/4115/stageScale", "datum": 67.389, "highestRecent": {"@id": "http://environment.data.gov.uk/flood-monitoring/id/stations/4115/stageScale/highestRecent", "dateTime": "2014-08-08T19:45:00", "value": 1.567}, "maxOnRecord": {"@id": "http://environment.data.gov.uk/flood-monitoring/id/stations/4115/stageScale/maxOnRecord", "dateTime": "1993-06-11T19:30:00", "value": 1.634}, "minOnRecord": {"@id": "http://environment.data.gov.uk/flood-monitoring/id/stations/4115/stageScale/minOnRecord", "dateTime": "1997-03-07T14:00:00", "value": 0.186}, "scaleMax": 2, "typicalRangeHigh": 1, "typicalRangeLow": 0.246}, "stationReference": "4115", "status": "http://environment.data.gov.uk/flood-monitoring/def/core/statusActive", "town": "Mansfield", "type": ["http://environment.data.gov.uk/flood-monitoring/def/core/SingleLevel", "http://environment.data.gov.uk/flood-monitoring/def/core/Station"], "wiskiID": "4115"}}""")
    site = """begin.asset
siteid=4115
longitude_[deg]=-1.164236
latitude_[deg]=53.166753
height_above_sea_level_[m]=
address=
city=Mansfield
country=UK
Postal_Code=
firstdate=1992-05-01
operator=
desc-url=http://environment.data.gov.uk/flood-monitoring/doc/reference
end.asset
"""
    sensor = """begin.asset
sensorid=4115-level-stage-i-15_min-mASD
provider=
serialnumber=
energysupply=
freqmaintenance=
sType=level
family=Water Level
data-acquisition-interval[min]=daily
firstdate=1992-05-01
datoz18-handle=
desc-url=
iot-import-IP=
iot-import-port=
iot-import-token=
iot-import-usrname=
iot-import-pwd=
iot-export-IP=
iot-export-port=
iot-export-token=
iot-export-usrname=
iot-export-pwd=
end.asset
"""

    def test_build_site(self):
        result = self.cls.build_site(self.test)
        self.assertEqual(self.site,str(result),"The return Site is not correct")

    def test_build_sensors(self):
        result = self.cls.build_sensors(self.test)
        self.assertEqual(self.sensor, str(result[0]), "The return Sensor is not correct")

    def test_generate_metadata(self):
        self.cls.generate_metadata(self.test)
        site_file = "assets/4115.txt"
        with open(site_file, "r+") as f:
            result = f.read()
        os.remove(site_file)
        self.assertEqual(self.site, result, "The saved Site is not correct")
        sensor_file = "assets/sensors/4115-level-stage-i-15_min-mASD.txt"
        with open(sensor_file, "r+") as f:
            result = f.read()
        os.remove(sensor_file)
        os.removedirs("assets/sensors")
        self.assertEqual(self.sensor, result, "The saved Sensor is not correct")

    def test_generate_metadata_csv(self):
        utils.build_dir("meta")
        self.cls.generate_metadata_csv([self.test])
        stations_file = "meta/stations.csv"
        expected = """@id|RLOIid|catchmentName|dateOpened|datumOffset|eaAreaName|eaRegionName|easting|label|lat|long|northing|notation|riverName|stageScale_@id|stageScale_datum|stageScale_highestRecent_@id|stageScale_highestRecent_dateTime|stageScale_highestRecent_value|stageScale_maxOnRecord_@id|stageScale_maxOnRecord_dateTime|stageScale_maxOnRecord_value|stageScale_minOnRecord_@id|stageScale_minOnRecord_dateTime|stageScale_minOnRecord_value|stageScale_scaleMax|stageScale_typicalRangeHigh|stageScale_typicalRangeLow|stationReference|status|town|type|wiskiID
http://environment.data.gov.uk/flood-monitoring/id/stations/4115|2146|Idle and Torne|1992-05-01||Midlands - Derbyshire Nottinghamshire and Leicestershire|Midlands|455970|Mansfield The Dykes|53.166753|-1.164236|363620|4115|River Maun|http://environment.data.gov.uk/flood-monitoring/id/stations/4115/stageScale|67.389|http://environment.data.gov.uk/flood-monitoring/id/stations/4115/stageScale/highestRecent|2014-08-08T19:45:00|1.567|http://environment.data.gov.uk/flood-monitoring/id/stations/4115/stageScale/maxOnRecord|1993-06-11T19:30:00|1.634|http://environment.data.gov.uk/flood-monitoring/id/stations/4115/stageScale/minOnRecord|1997-03-07T14:00:00|0.186|2|1|0.246|4115|http://environment.data.gov.uk/flood-monitoring/def/core/statusActive|Mansfield|['http://environment.data.gov.uk/flood-monitoring/def/core/SingleLevel', 'http://environment.data.gov.uk/flood-monitoring/def/core/Station']|4115
"""
        with open(stations_file, "r+") as f:
            result = f.read()
        os.remove(stations_file)
        self.assertEqual(expected, result, "The saved Site CSV file is not correct")
        sensors_file = "meta/sensors.csv"
        expected = """@id|datumType|label|latestReading_@id|latestReading_date|latestReading_dateTime|latestReading_value|notation|parameter|parameterName|period|qualifier|station|stationReference|type|unit|unitName|valueType
http://environment.data.gov.uk/flood-monitoring/id/measures/4115-level-stage-i-15_min-mASD|http://environment.data.gov.uk/flood-monitoring/def/core/datumASD|Mansfield The Dykes LVL - level-stage-i-15_min-mASD|http://environment.data.gov.uk/flood-monitoring/data/readings/4115-level-stage-i-15_min-mASD/2020-03-22T18-00-00Z|2020-03-22|2020-03-22T18:00:00Z|0.308|4115-level-stage-i-15_min-mASD|level|Water Level|900|Stage|http://environment.data.gov.uk/flood-monitoring/id/stations/4115|4115|['http://environment.data.gov.uk/flood-monitoring/def/core/Measure', 'http://environment.data.gov.uk/flood-monitoring/def/core/WaterLevel']|http://qudt.org/1.1/vocab/unit#Meter|mASD|instantaneous
"""
        with open(sensors_file, "r+") as f:
            result = f.read()
        os.remove(sensors_file)
        os.removedirs("meta")
        self.assertEqual(expected, result, "The saved Sensor CSV file is not correct")

if __name__ == '__main__':
    unittest.main()

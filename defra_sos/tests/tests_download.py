"""
Run the test suite for download
"""

import logging
import unittest
import datetime
import download

LOGGER = logging.getLogger(__name__)

class TestDownload(unittest.TestCase):

    # def test_get_stations(self):
    #     date = datetime.datetime.strptime("2020-03-10", '%Y-%m-%d')
    #     od = "flood.csv"
    #     k = 25
    #     um = True
    #     om = "meta"
    #     v = True
    #     ad = "assets"
    #     cls = download.FloodHarvestor(date=date, distance=k, update_meta=um, output_meta=om, logger=LOGGER)
    #     station = next(cls.get_stations()).get("items","{}").get("@id","")
    #     expected = True
    #     result = True if "http://environment.data.gov.uk/flood-monitoring/id/stations" in station else False
    #     self.assertEqual(result, expected, "'http://environment.data.gov.uk/flood-monitoring/id/stations' "
    #                      "should be returned station".format(expected))

    def test_get_data(self):
        date = datetime.datetime.strptime("2020-03-10", '%Y-%m-%d')
        od = "flood.csv"
        k = 25
        um = True
        om = "meta"
        v = True
        ad = "assets"
        cls = download.FloodHarvestor(date=date, distance=k, update_meta=um, output_meta=om, logger=LOGGER)
        station = next(cls.get_stations())
        row = next(cls.get_data([station]))
        self.assertTrue(row["dateTime"] == "2020-03-10T00:00:00Z", "Date is not correct")
        # self.assertTrue("http://environment.data.gov.uk/flood-monitoring/id/measures/" in row["measure"],
        #                 "Measure is not correct {}".format(row["measure"]))
        # self.assertTrue(len(row["value"]) > 0, "Value is not correct {}".format(row["value"]))
        # self.assertTrue(float(abs(row["lat"])) > 0, "Latitude is not correct {}".format(row["lat"]))
        # self.assertTrue(float(abs(row["long"])) > 0, "Longitude is not correct {}".format(row["long"]))
        # self.assertTrue("http://environment.data.gov.uk/flood-monitoring/id/stations" in row["station"],
        #                 "Station is not correct {}".format(row["station"]))
        # self.assertTrue(len(row["parameter_name"]) > 0, "Parameter name is not correct {}".format(row["parameter_name"]))
        # self.assertTrue(len(row["unit"]) > 0, "Unit is not correct {}".format(row["unit"]))


    # def test_transform(self):
    #     date = datetime.datetime.strptime("2020-03-10", '%Y-%m-%d')
    #     od = "flood.csv"
    #     k = 25
    #     um = True
    #     om = "meta"
    #     v = True
    #     ad = "assets"
    #     cls = download.FloodHarvestor(date=date, distance=k, update_meta=um, output_meta=om, logger=LOGGER)
    #     station = next(cls.get_stations())
    #     row = next(cls.get_data([station]))
    #     transformed_row = cls.transform(row)
    #     self.assertTrue(transformed_row["timestamp"] == "2020-03-10T00:00:00Z",
    #                     "Timestamp is not correct {}".format(transformed_row["timestamp"]))


if __name__ == '__main__':
    unittest.main()

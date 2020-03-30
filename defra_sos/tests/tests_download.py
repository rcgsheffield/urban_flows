"""
Run the test suite for download
"""

import logging
import unittest
import datetime

import download
import http_session

LOGGER = logging.getLogger(__name__)


class TestDownload(unittest.TestCase):

    def test_get_stations(self):
        date = datetime.date(2020, 3, 10)
        od = "defra_sos.csv"
        k = 25
        um = True
        om = "meta"
        v = True
        ad = "assets"

        cls = download.DEFRASOSHarvestor(date=date, distance=k, update_meta=um, output_meta=om, logger=LOGGER)
        station = next(cls.get_stations())  # .get("items","{}").get("@id","")

        self.assertTrue("properties" in station, "station has no 'properties' key")

    def test_get_data(self):
        date = datetime.datetime.strptime("2020-03-10", '%Y-%m-%d')
        od = "flood.csv"
        k = 50
        um = True
        om = "meta"
        v = True
        ad = "assets"
        station = http_session.DEFRASOSSession().call("https://uk-air.defra.gov.uk/sos-ukair/api/v1/", "stations/1267")
        cls = download.DEFRASOSHarvestor(date=date, distance=k, update_meta=um, output_meta=om, logger=LOGGER)
        row = next(cls.get_data([station]))
        self.assertTrue(str(row["timestamp"])[0:3] == "158", "Date is not correct {}"
                        .format(str(row["timestamp"])[0:3]))
        self.assertTrue(str(row["station"]) == "1267", "Station is not correct {}".format(row["station"]))
        self.assertTrue(len(str(row["value"])) > 0, "Value is not correct {}".format(row["value"]))
        self.assertTrue(float(abs(row["lat"])) > 0, "Latitude is not correct {}".format(row["lat"]))
        self.assertTrue(float(abs(row["long"])) > 0, "Longitude is not correct {}".format(row["long"]))
        self.assertTrue(len(row["parameter_name"]) > 0, "Parameter name is not correct {}"
                        .format(row["parameter_name"]))
        self.assertTrue(len(row["unit"]) > 0, "Unit is not correct {}".format(row["unit"]))

    def test_transform(self):
        date = datetime.datetime.strptime("2020-03-10", '%Y-%m-%d')
        od = "flood.csv"
        k = 50
        um = True
        om = "meta"
        v = True
        ad = "assets"
        station = http_session.DEFRASOSSession().call("https://uk-air.defra.gov.uk/sos-ukair/api/v1/", "stations/1267")
        cls = download.DEFRASOSHarvestor(date=date, distance=k, update_meta=um, output_meta=om, logger=LOGGER)
        row = next(cls.get_data([station]))
        transformed_row = cls.transform(row)
        self.assertTrue(str(transformed_row["timestamp"]) == "2020-03-09 00:00:00",
                        "Timestamp is not correct {}".format(transformed_row["timestamp"]))


if __name__ == '__main__':
    unittest.main()

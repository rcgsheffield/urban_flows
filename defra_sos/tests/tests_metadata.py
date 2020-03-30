import json
import logging
import unittest

import metadata

LOGGER = logging.getLogger(__name__)


class TestMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.harvester = metadata.DEFRASOSHarvesterMeta("meta")

        with open('tests/south_kirkby_station.json') as file:
            cls.station = json.load(file)

        with open('tests/south_kirkby_timeseries.json') as file:
            cls.timeseries = json.load(file)

        with open('tests/south_kirkby_site.txt') as file:
            cls.site = file.read()

        with open('tests/south_kirkby_sensor.txt') as file:
            cls.sensor = file.read()

    def test_build_site(self):
        result = self.harvester.build_site(self.station)

        self.assertEqual(self.site, str(result), "The return Site is not correct")

    def test_build_sensors(self):
        sensor = self.harvester.build_sensor(self.timeseries)

        self.assertEqual(self.sensor, str(sensor), "The return Sensor is not correct")

    def test_generate_metadata(self):
        site = self.harvester.generate_metadata(self.station)
        self.assertEqual(self.site, site, "The saved Site is not correct")

        result = None
        self.assertEqual(self.sensor, result, "The saved Sensor is not correct")


if __name__ == '__main__':
    unittest.main()

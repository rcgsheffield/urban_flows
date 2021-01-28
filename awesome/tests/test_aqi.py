import logging
import unittest

import aqi.daqi

LOGGER = logging.getLogger(__name__)

DAQI_POLLUTANTS = dict(
    ozone=115,
    nitrogen_dioxide=201,
    sulphur_dioxide=887,
    particles_25=49.5,
    particles_10=0.01,
)


class DAQITestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)

        self.aqi = aqi.daqi.DailyAirQualityIndex(**DAQI_POLLUTANTS)

        LOGGER.info(self.aqi)

    def test_banding(self):
        for pollutant in DAQI_POLLUTANTS.keys():
            value = self.aqi.pollutant_indexes[pollutant]

            LOGGER.info("%s = %s", pollutant, value)

            self.assertIsInstance(value, int)
            self.assertGreaterEqual(value, 1)
            self.assertLessEqual(value, 10)

    def test_pollutants(self):
        for pollutant in DAQI_POLLUTANTS.keys():
            value = self.aqi.pollutants[pollutant]

            LOGGER.info("%s = %s", pollutant, value)

            self.assertIsInstance(value, (int, float))

    def test_index(self):
        value = self.aqi.index

        LOGGER.info(value)

        self.assertIsInstance(value, int)

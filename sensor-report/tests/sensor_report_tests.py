import os
import unittest

import pandas as pd

from data_service.handler import DataHandler

TEST_DATA_DIR = os.path.join(os.getcwd(), 'tests', 'files')
OUTPUT_PATH = 'output.csv'

AMBER_THRESHOLD = 0.8

class TestDataHandler(unittest.TestCase):

    def assertDataframeEqual(self, a, b):
        try:
            pd.testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(str(e)) from e

    def test_that_the_rag_calculator_returns_the_correct_string(self):

        self.assertEqual(DataHandler.calculate_rag(0.7, AMBER_THRESHOLD), "Red")
        self.assertEqual(DataHandler.calculate_rag(0.8, AMBER_THRESHOLD), "Amber")
        self.assertEqual(DataHandler.calculate_rag(1, AMBER_THRESHOLD), "Green")

    def test_that_report_returns_correct_output(self):
        handler = DataHandler(TEST_DATA_DIR, OUTPUT_PATH)
        handler.process_input()

        columns = ["site_id", "sensor_id", "measure", "uptime", "RAG"]
        data = ([["S0001", 711, "AQ_CO", 1.0, "Green"],
                 ["S0001", 711, "AQ_NO", 1.0, "Green"],
                 ["S0001", 711, "AQ_NO2", 1.0, "Green"],
                 ["S0001", 711, "AQ_NOISE", 1.0, "Green"],
                 ["S0001", 711, "ID_MAIN", 1.0, "Green"],
                 ["S0001", 711, "MET_RH", 1.0, "Green"],
                 ["S0001", 711, "MET_TEMP", 1.0, "Green"],
                 ["S0015", 2003150, "AQ_NO", 0.8, "Amber"],
                 ["S0015", 2003150, "AQ_NO2", 1.0, "Green"],
                 ["S0015", 2003150, "AQ_O3", 1.0, "Green"],
                 ["S0015", 2003150, "ID_MAIN", 1.0, "Green"],
                 ["S0015", 2003150, "MET_AP", 1.0, "Green"],
                 ["S0015", 2003150, "MET_RH", 0.5, "Red"],
                 ["S0015", 2003150, "MET_TEMP", 1.0, "Green"]])

        actual = handler.create_report(serialise=False, amber_threshold=AMBER_THRESHOLD)
        expected = pd.DataFrame(data, columns=columns)

        self.assertDataframeEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

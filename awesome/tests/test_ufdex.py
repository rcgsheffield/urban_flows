import unittest
import datetime
import logging

import ufdex

LOGGER = logging.getLogger(__name__)


class UrbanFlowsDataExtractorTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.WARNING)
        now = datetime.datetime.now()
        self.query = ufdex.UrbanFlowsQuery(
            time_period=[now - datetime.timedelta(days=1), now],
            sensors={'20926'})

    def test_query(self):
        for row in self.query():
            LOGGER.debug(row)

    def test_time_periods(self):
        n_periods = 3
        start = datetime.datetime(2020, 1, 1)
        freq = datetime.timedelta(days=10)
        end = start + n_periods * freq

        time_period_count = 0
        for t0, t1 in ufdex.UrbanFlowsQuery.generate_time_periods(
                start=start, end=end, freq=freq):
            time_period_count += 1
            LOGGER.debug("%s %s", t0, t1)

            # Ensure no time periods are of zero duration
            period_seconds = (t1 - t0).total_seconds()
            self.assertGreater(period_seconds, 0.0)

        # Check we get the expected number of time periods
        self.assertEqual(time_period_count, n_periods)

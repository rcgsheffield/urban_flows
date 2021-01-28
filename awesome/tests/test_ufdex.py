import unittest
import datetime
import logging

import ufdex

LOGGER = logging.getLogger(__name__)


class UrbanFlowsDataExtractorTestCase(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.WARNING)
        now = datetime.datetime.now()
        self.query = ufdex.UrbanFlowsQuery(time_period=[now - datetime.timedelta(days=2), now, ], sensors={'20926'})

    def test_query(self):
        for row in self.query(use_http=True):
            LOGGER.debug(row)

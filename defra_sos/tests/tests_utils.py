"""
Run the test suite for utils
"""

import logging
import unittest
import os
import argparse
import datetime

import utils

LOGGER = logging.getLogger(__name__)


class TestUtils(unittest.TestCase):

    def test_build_dir(self):
        param1 = "param1"
        param2 = "param2"
        utils.build_dir("{}/{}".format(param1, param2))
        expected = "Output dir for meta is build"
        result = expected if os.path.exists("{}/{}".format(param1, param2)) else "The dir does not exists"
        os.rmdir("{}/{}".format(param1, param2))
        os.rmdir(param1)

        self.assertEqual(result, expected, "Should be '{}'".format(expected))

    def test_build_output_dir_for_meta(self):
        param1 = "param1"
        param2 = "param2"
        utils.build_output_dir_for_meta(param1, param2)
        expected = "Output dir for meta is build"
        result = expected if os.path.exists("{}/{}".format(param1, param2)) else "The dir does not exists"
        os.rmdir("{}/{}".format(param1, param2))
        os.rmdir(param1)

        self.assertEqual(result, expected, "Should be '{}'".format(expected))

    def test_build_output_dir_for_data(self):
        param1 = "param1"
        param2 = "param2"
        utils.build_output_dir_for_data(param1, param2)
        expected = "Output dir for meta is build"
        result = expected if os.path.exists("{}/{}".format(param1, param2)) else "The dir does not exists"
        os.rmdir("{}/{}".format(param1, param2))
        os.rmdir(param1)

        self.assertEqual(result, expected, "Should be '{}'".format(expected))

    def test_get_args(self):
        param1 = "description"
        args = "-d 2020-03-10 -od flood.csv -k 25 -um True -om meta -v True -ad assets".split(" ")
        result = utils.get_args(param1, args)
        expected = argparse.Namespace(assets_dir='assets', date=datetime.datetime(2020, 3, 10, 0, 0),
                                      distance=25, output_data='flood.csv', output_meta='meta', update_meta=True,
                                      verbose=True)

        self.assertEqual(result, expected, "The returned namespace should be correct'".format(expected))


if __name__ == '__main__':
    unittest.main()

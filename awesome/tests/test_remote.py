import unittest

import remote

HOST = 'ufdev'


class RemoteTestCase(unittest.TestCase):
    def setUp(self):
        username = input('Enter username for {host}: '.format(host=HOST))
        self.remote_host = remote.RemoteHost(HOST, username=username)

    def tearDown(self):
        self.remote_host.close()

    def test_echo(self):
        for x in self.remote_host.execute_decode('echo Hello world!'):
            print(x)

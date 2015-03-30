__author__ = 'spacy'

import unittest

from protocol_testing.tester_config_handler import TesterConfigHandler


class TestTesterConfigHandler(unittest.TestCase):

    def setUp(self):
        self.filename = "../test_config.json"
        self.config_handler = TesterConfigHandler(self.filename)

    def test_get_node_names(self):
        names = self.config_handler.get_node_names()
        self.assertNotEqual(False, names)
        self.assertEqual(2, len(names))


if __name__ == '__main__':
    unittest.main()

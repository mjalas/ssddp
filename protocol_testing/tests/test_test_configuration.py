
import unittest

from protocol_testing.config_test_file import TestConfiguration
from protocol_testing.config_test_file import ConfigurationNode


class TestTestConfiguration(unittest.TestCase):
    def test_read_config_from_file(self):
        filename = "test_config.json"
        configuration = TestConfiguration.read_config_from_file(filename)
        self.assertEqual(2, len(configuration.nodes))


if __name__ == '__main__':
    unittest.main()

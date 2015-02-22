import unittest
import time
from datetime import datetime
from message.timestamp import Timestamp


class TestTimestamp(unittest.TestCase):
    """

    """

    def setUp(self):
        pass

    def test_create_timestamp(self):
        self.assertAlmostEqual(time.time(), Timestamp.create_timestamp())

    def test_timestamp_to_string(self):
        timestamp = time.time()
        self.assertEqual(datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f'),
                         Timestamp.timestamp_to_string(timestamp))


if __name__ == '__main__':
    unittest.main()

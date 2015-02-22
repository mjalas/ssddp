from datetime import datetime
import time


class Timestamp(object):
    """
    Helper class for handling timestamps.
    """
    @staticmethod
    def create_timestamp():
        return time.time()

    @staticmethod
    def timestamp_to_string(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

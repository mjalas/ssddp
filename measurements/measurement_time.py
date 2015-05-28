from datetime import datetime
import time
from message.timestamp import Timestamp


class MeasurementTimeGetter(object):
    """

    """
    def __init__(self):
        pass

    def now(self):
        """
        Method for getting the current time. The method can either return get_datetime() or get_timestamp().
        This way the time format can easily be changed to fit requirements.
        New methods can also easily be added for new time formats.
        :return: Current time in format depending on method call.
        """
        return self.get_datetime()

    def get_time(self):
        """
        Method for getting the time. The method can either return get_datetime() or get_timestamp().
        This way the time format can easily be changed to fit requirements.
        New methods can also easily be added for new time formats.
        :return: Current time in format depending on method call.
        """
        return self.get_datetime()

    @staticmethod
    def get_datetime():
        """

        :return: current time in datetime format
        """
        return datetime.now()

    @staticmethod
    def get_timestamp():
        """

        :return: timestamp of current time.
        """
        return Timestamp.create_timestamp()


class MeasurementTimer(object):
    """
    A time class for measurements.
    """
    def __init__(self):
        self._duration = 0
        self._timer_started = time.clock()

    def start(self):
        self._timer_started = time.clock()

    def stop(self):
        self._duration = time.clock() - self._timer_started

    def get_duration(self):
        return self._duration


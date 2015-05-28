from datetime import datetime, timedelta, time

from measurements.measurement_time import MeasurementTimeGetter
from measurements.measurementdata import MeasurementData
from measurements.measurementdata import DurationMeasurementData


class MeasurementLogger(object):
    """
    Printer for SSDDP nodes.
    """

    def __init__(self, log_file="protocol_test.log"):
        self.log_file = log_file
        self.log_messages = True
        self.time_getter = MeasurementTimeGetter()
        with open(log_file, 'w') as f:
            line = str(self.get_time()) + ": Created logfile."
            f.write(line)

    def log(self, message, node_name):
        with open(self.log_file, 'a') as f:
            tmp = str(self.get_time()) + ": '" + str(node_name) + "': " + str(message) + "\n"
            f.write(tmp)
            f.flush()

    def get_time(self):
        self.time_getter.get_time()


class MeasurementDataLogger(object):
    def __init__(self, log_file="protocol_test.log"):
        self.log_file = log_file
        with open(log_file, 'w') as f:
            line = str(datetime.now()) + ": Created measurement result file.\n"
            f.write(line)

    def log(self, data):
        if isinstance(data, MeasurementData):
            if isinstance(data, DurationMeasurementData):
                line = "{0}: '{1}': {2} (duration: {3})".format(data.time_of_event, data.node_name, data.message, data.duration)
            else:
                line = "{0}: '{1}': {2}".format(data.time_of_event, data.node_name, data.message)
            with open(self.log_file, 'a') as f:
                tmp = line + "\n"
                f.write(tmp)
                f.flush()


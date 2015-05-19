import time
import abc


class MeasurementDataStringCreator(object):
    """
    Class with methods for creating strings to display measurement data.
    """
    def __init__(self, node_name):
        self.node_name = node_name

    def all_nodes_discovered(self, node_count, duration):
        return "{0}: All {1} nodes discovered after {2} seconds".format(self.node_name, node_count, duration)

    def description_request_average(self, average):
        return "{0}: Average duration for description request is {1} seconds".format(self.node_name, average)


class MeasurementDataWriter(object):
    """
    Base class for measurement data writing.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, node_name):
        self.string_creator = MeasurementDataStringCreator(node_name)

    @abc.abstractmethod
    def log(self, message):
        """Logs the messages according to inherited class"""

    def discovery_duration(self, node_count, duration):
        message = self.string_creator.all_nodes_discovered(node_count, duration)
        self.log(message)

    def average_description_request(self, average):
        message = self.string_creator.description_request_average(average)
        self.log(message)


class MeasurementDataPrinter(MeasurementDataWriter):
    """
    Class for printing measurement data to screen.
    """

    def __init__(self, node_name):
        super().__init__(node_name)

    def log(self, message):
        print(message)


class MeasurementDataLogger(MeasurementDataWriter):
    """
    Class for logging measurement data to file.
    """

    def __init__(self, node_name):
        super().__init__(node_name)

    def log(self, message):
        pass


class MeasurementData(object):
    """
    Class for holding measurement data that can be shared to managers in SSDDP app.
    """
    def __init__(self, node_name, nodes_in_test, log=False):
        self.test_started = None
        self.test_ended = None
        self.discovery_started = None
        self.all_nodes_discovered = None
        self.node_name = node_name
        self.nodes_in_test = nodes_in_test
        self.node_count = 0
        self.description_durations = []
        if log:
            self.printer = MeasurementDataLogger(node_name)
        else:
            self.printer = MeasurementDataPrinter(node_name)

    def start_test(self):
        self.test_started = time.clock()

    def end_test(self):
        self.test_ended = time.clock()

    def discovery_started(self):
        self.discovery_started = time.clock()

    def discovered_new_node(self):
        self.node_count += 1

    def node_disappeared(self):
        self.node_count -= 1

    def check_if_all_nodes_found(self):
        if self.node_count == self.nodes_in_test:
            end = time.clock()
            self.all_nodes_discovered = end - self.discovery_started
            return True
        return False

    def add_description_duration(self, duration):
        self.description_durations.append(duration)

    def display_discovery_duration(self):
        self.printer.discovery_duration(self.nodes_in_test, self.all_nodes_discovered)

    def display_description_average(self):
        count = len(self.description_durations)
        average = sum(self.description_durations)/count
        self.printer.average_description_request(average)
import time
import abc
from json import JSONEncoder, JSONDecoder


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
        self.node_name = node_name

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

    def __init__(self, node_name, printer=None, measurement_logger=None):
        super().__init__(node_name)
        self.printer = printer
        self.measurement_logger = measurement_logger

    def log(self, message):
        if self.measurement_logger:
            self.measurement_logger.log(message, self.node_name)
        if self.printer:
            self.printer.log(message)
        else:
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
    def __init__(self, node_name, nodes_in_test, printer=None, log=False, measurement_logger=None):
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
            self.printer = MeasurementDataPrinter(node_name, printer, measurement_logger)

    def start_test(self):
        self.test_started = time.clock()

    def end_test(self):
        self.test_ended = time.clock()

    def start_discovery(self):
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


class MeasurementDataEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, MeasurementData):
            d = {'test_started': o.test_started,
                 'test_ended': o.test_ended,
                 'discovery_started': o.discovery_started,
                 'node_name': o.node_name,
                 'node_count': o.node_count,
                 'nodes_in_test': o.nodes_in_test,
                 'description_durations': o.description_durations}
            return d
        else:
            raise TypeError("Given argument is not of type Node!")


class MeasurementDataDecoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        node_name = d['node_name']
        node_count = d['node_count']
        test_started = d['test_started']
        test_ended = d['test_ended']
        discovery_started = d['discovery_started']
        nodes_in_test = d['nodes_in_test']
        description_durations = d['description_durations']
        m = MeasurementData(node_name, nodes_in_test)
        m.test_started = test_started
        m.test_ended = test_ended
        m.discovery_started = discovery_started
        m.node_count = node_count
        m.description_durations = description_durations
        return m
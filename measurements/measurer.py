
from measurements.measurementdata import MeasurementDataContainer
from measurements.measurementdata import MeasurementData, DurationMeasurementData
from measurements.measurement_time import MeasurementTimer, MeasurementTimeGetter
from printers_and_loggers.measurement_logger import MeasurementDataLogger




class Measurer(object):
    """
    Class for handling performance measuring.
    """
    def __init__(self, node_in_test, logger):
        """

        :param logger: logging handler
        :return:
        """
        self.nodes_in_test = 0
        self.data_container = MeasurementDataContainer(node_in_test)
        self.timer = MeasurementTimer()
        self.time_getter = MeasurementTimeGetter()
        self.logger = logger
        self.nodes = {}
        self.discovery_started = self.time_getter.now()
        self.discovery_duration = None

    nodes_to_find = 'nodes_to_find'
    nodes_found = 'nodes_found'

    def add_node(self, node_name, nodes_in_network):
        node_data = {self.nodes_to_find: nodes_in_network, self.nodes_found: 0}
        self.nodes[node_name] = node_data

    def set_nodes_in_network_for_node(self, node_name, node_count):
        self.nodes[node_name][self.nodes_to_find] = node_count

    def get_nods_to_find(self, node_name):
        return self.nodes[node_name][self.nodes_to_find]

    def log(self, message, node_name):
        self.logger.log(message, node_name)

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()

    def get_last_duration(self):
        self.timer.get_duration()

    def add_data(self, data):
        self.data_container.add_data(data)

    def add_duration(self, node_name, message, duration=None):
        if duration:
            data = DurationMeasurementData(node_name, message, self.time_getter.now(), duration)
        else:
            data = DurationMeasurementData(node_name, message, self.time_getter.now(), self.get_last_duration())
        self.add_data(data)

    def add_time_event(self, node_name, time_of_event, message):
        data = MeasurementData(node_name, message, time_of_event)
        self.add_data(data)

    def add_event(self, node_name, message):
        data = MeasurementData(node_name, message, self.time_getter.now())
        self.add_data(data)

    def log_all_data(self, log_file):
        data_logger = MeasurementDataLogger(log_file)
        for data in self.data_container.measurement_data:
            data_logger.log(data)

    def node_shutdown(self, node_name):
        message = "Node shutdown."
        data = MeasurementData(node_name, message, self.time_getter.now())
        self.add_data(data)

    def start_discovery(self, node_name):
        self.discovery_started = self.time_getter.now()
        message = "Discovery started."
        data = MeasurementData(node_name, message, self.time_getter.now())
        self.add_data(data)

    def discovered_new_node(self, node_name, new_node_name):
        message = "Discovered new node '{0}'".format(new_node_name)
        self.add_event(node_name, message)
        node_data = self.nodes[node_name]
        nodes_to_find = node_data[self.nodes_to_find]
        nodes_found = node_data[self.nodes_found] + 1
        #print("{0}: found {1}/{2} nodes".format(node_name, nodes_found, nodes_to_find))
        node_data[self.nodes_found] = nodes_found

        if nodes_to_find == nodes_found:
            discovery_duration = self.time_getter.now() - self.discovery_started
            self.discovery_duration = discovery_duration
            message = "All nodes discovered."
            self.add_duration(node_name, message, discovery_duration)
            return True
        return False

    def description_duration(self, node_name, duration):
        message = "Description sent and received"
        self.add_duration(node_name, message, duration)

    def discovered_node_missing(self, node_name, missing_node_name):
        message = "'{0}' has leaved network.".format(missing_node_name)
        self.add_event(node_name, message)
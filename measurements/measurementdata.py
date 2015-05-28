

class MeasurementDataContainer(object):
    """
    Class for holding measurement data that can be shared to managers in SSDDP app.
    """
    def __init__(self, nodes_in_test):
        self.test_started = None
        self.test_ended = None
        self.nodes_in_test = nodes_in_test
        self.nodes_active = 0
        self.measurement_data = []

    def increase_active_nodes(self):
        self.nodes_active += 1

    def decrease_active_nodes(self):
        if self.nodes_active > 0:
            self.nodes_active -= 1

    def add_data(self, data):
        if not isinstance(data, MeasurementData):
            raise TypeError("data not of type NodeMeasurementData")
        self.measurement_data.append(data)


class MeasurementData(object):
    """
    Base class for storing measurement data
    """
    def __init__(self, node_name, message, time_of_event):
        self.node_name = node_name
        self.message = message
        self.time_of_event = time_of_event


class DurationMeasurementData(MeasurementData):
    """
    Class for storing duration measurement data
    """
    def __init__(self, node_name, message, time_of_event, duration):
        super().__init__(node_name, message, time_of_event)
        self.duration = duration




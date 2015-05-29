import logging
from app.ssddp_v2 import SSDDP
from measurements.measurer import Measurer
from printers_and_loggers.measurement_logger import MeasurementLogger
from service.service_list import ServiceList, Service

nodes_in_network = 10
node_name = "test_node"
measurement_log = node_name + "_measurement.log"


logging.basicConfig(
    format="{levelname:<8} {name:>30}:{funcName:<20}: {message}",
    style='{',
    level=logging.DEBUG,
)

if __name__ == "__main__":

    logger = MeasurementLogger(measurement_log)
    measurer = Measurer(nodes_in_network, logger)
    measurer.add_node(node_name, nodes_in_network)
    service_list_file = "static_node_messages/service_list.json"
    app = SSDDP(node_name, measurer, service_list_file=service_list_file)
    try:
        app.start()
    except KeyboardInterrupt:
        app.stop()
        print("User interrup")

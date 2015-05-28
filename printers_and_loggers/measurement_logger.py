from printers_and_loggers.logger import Logger


class MeasurementLogger(Logger):
    """
    Printer for SSDDP nodes.
    """

    def __init__(self, log_file):
        super().__init__(log_file)

    def log(self, message, node_name):
        super().log(message, node_name)


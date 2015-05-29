import logging

from datetime import datetime
from message.timestamp import Timestamp
from printers_and_loggers.printer import BasePrinter


class Logger(object):
    """
    Base class for loggers.
    """
    def __init__(self, log_file="protocol_test.log"):
        self.log_file = log_file
        with open(log_file, 'w') as f:
            line = str(datetime.now()) + ": Created logfile.\n"
            f.write(line)

    def log(self, message):
        with open(self.log_file, 'a') as f:
            tmp = str(datetime.now()) + ": " + str(message) + "\n"
            f.write(tmp)
            f.flush()

    def debug(self, message):
        message = "Debug(" + message + ")"
        self.log(message)

    def info(self, message):
        self.log(message)

    def error(self, message):
        message = "Error(" + message + ")"
        self.log(message)

    def warning(self, message):
        message = "Warning(" + message + ")"
        self.log(message)


class NodeLogger(Logger):
    """
    Logger class for SSDDP nodes
    """
    def __init__(self, node_name, log_file, debug_mode=False):
        super().__init__(log_file)
        self.node_name = node_name
        self.debug_mode = debug_mode
        self.logger = logging.getLogger(self.node_name + ": " + __name__)

    def log(self, message):
        message = self.node_name + ": " + str(message)
        super().log(message)

    def debug(self, message):
        if self.debug_mode:
            self.logger.debug(message)
            super().debug(message)

    def info(self, message):
        self.logger.info(message)
        super().info(message)

    def error(self, message):
        self.logger.error(message)
        super().error(message)

    def warning(self, message):
        self.logger.warning(message)
        super().warning(message)


class NodePrinterLogger(Logger):
    """
    Node logger with ui printing
    """
    def __init__(self, node_name, log_file, debug_mode=False):
        super().__init__(log_file)
        self.node_name = node_name
        self.debug_mode = debug_mode
        self.printer = BasePrinter()

    def log(self, message):
        message = self.node_name + ": " + str(message)
        super().log(message)
        self.printer.display(message)

    def debug(self, message):
        if self.debug_mode:
            super().debug(message)
            self.printer.display(message)

    def info(self, message):
        super().info(message)
        self.printer.display(message)

    def error(self, message):
        message = "Error(" + message + ")"
        super().error(message)
        self.printer.display(message)
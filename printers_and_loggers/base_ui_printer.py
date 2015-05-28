from printers_and_loggers.test_printer import TestPrinter


class BaseUIPrinter(object):
    """
    Base logger class
    """
    def __init__(self, log_file, display=True, debug=False, log_messages=False):
        self.debug = debug
        self.display_outputs = display
        self.printer = TestPrinter(log_file)
        self.log_messages = log_messages

    def display(self, message):
        if self.display_outputs:
            self.printer.display(message)

    def log(self, message, append=True):
        self.printer.log(message, append)


from datetime import datetime
from message.timestamp import Timestamp


class BasePrinter(object):
    """
    """
    def __init__(self):
        pass

    def log(self, message):
        self.display(message)

    @staticmethod
    def display(message):
        print(message)


class Printer(BasePrinter):
    """
    """
    def __init__(self, log_file="protocol_test.log", print_to_ui=False):
        super().__init__()
        self.log_file = log_file
        self.print_to_ui = print_to_ui
        self.log_messages = True
        with open(log_file, 'w') as f:
            line = str(Timestamp.create_timestamp()) + ": Created logfile."
            f.write(line)

    def log(self, message):
        with open(self.log_file, 'a') as f:
            tmp = str(datetime.now()) + ": " + str(message) + "\n"
            f.write(tmp)
            f.flush()
        if self.print_to_ui:
            super().display(message)

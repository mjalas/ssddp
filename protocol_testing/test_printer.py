from datetime import datetime


class TestPrinter(object):
    """
    """
    def __init__(self, log_file="protocol_test.log"):
        self.log_file = log_file
        self.log_messages = True

    def log(self, message, append=True):
        mode = 'w'
        if append:
            mode = 'a'

        with open(self.log_file, mode) as f:
            tmp = str(datetime.now()) + ": " + message + "\n"
            f.write(tmp)
            f.flush()

    def display(self, message):
        if self.log_messages:
            self.log(message)
        print(message)

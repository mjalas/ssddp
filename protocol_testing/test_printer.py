from datetime import datetime


class TestPrinter(object):
    """
    """
    def __init__(self, log_file="protocol_test.log"):
        self.log_file = log_file

    def log(self, message, append=True):
        mode = 'w'
        if append:
            mode = 'a'

        with open(self.log_file, mode) as f:
            tmp = str(datetime.now()) + ": " + message
            f.write(tmp)
            f.flush()

    def display(self, message, log=False):
        if log:
            self.log(message)
        print(message)
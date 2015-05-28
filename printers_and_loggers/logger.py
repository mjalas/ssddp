from datetime import datetime
from message.timestamp import Timestamp


class Logger(object):
    """
    Base class for loggers.
    """
    def __init__(self, log_file="protocol_test.log"):
        self.log_file = log_file
        self.log_messages = True
        with open(log_file, 'w') as f:
            line = str(Timestamp.create_timestamp()) + ": Created logfile."
            f.write(line)

    def log(self, message, object_name):
        with open(self.log_file, 'a') as f:
            tmp = str(datetime.now()) + ": '" + str(object_name) + "': " + str(message) + "\n"
            f.write(tmp)
            f.flush()






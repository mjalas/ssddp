from os import path, utime

from message.timestamp import Timestamp


class LogFileHandler(object):


    @staticmethod
    def create_file_if_not_available(file_path):
        if not path.exists(file_path):
            try:
                with open(file_path, 'w'):
                    utime(file_path, None)
            except FileNotFoundError:
                print(__file__)


    @staticmethod
    def create_log_file(base_filename):
        filename = base_filename + "_" + str(Timestamp.create_timestamp()).replace(".", "_") + ".log"
        LogFileHandler.create_file_if_not_available(filename)
        return filename

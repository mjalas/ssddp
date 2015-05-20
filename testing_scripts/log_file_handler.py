from os import path, utime

from message.timestamp import Timestamp


class LogFileHandler(object):

    @staticmethod
    def create_file_if_not_available(file_path):
        if not path.exists(file_path):
            with open(file_path, 'a'):
                utime(file_path, None)

    @staticmethod
    def create_log_file(base_filename):
        filename = base_filename + "_" + str(Timestamp.create_timestamp()).replace(".", "_") + ".log"
        LogFileHandler.create_file_if_not_available(filename)
        return filename
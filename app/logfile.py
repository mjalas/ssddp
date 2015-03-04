

class Logfile(object):
    def __init__(self, filepath):

        # output file
        if filepath:
            self.file = open(logfile_path, "w")
        else:
            self.file = None

    def log(self, message):
        self.log_file.write(message)

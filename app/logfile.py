

class Logfile(object):
    """
    Class for logging important statistics to a file
    """
    def __init__(self, file_path):

        # output file
        if file_path:
            self.file = open(file_path, "w")
        else:
            self.file = None

    def log(self, message):

        if self.file:
            self.file.write(message)
            self.file.flush()

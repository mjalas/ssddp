

class Logfile(object):
    """
    Class for logging important statistics to a file.
    Metrics to measure:

        ● Discovery time of network:
            A new node discovering all the nodes
            and services of the network

        ● Discovery time of a node:
            How quickly is a node connecting to the
            network detected by already present nodes

        ● Disappearing node detection time:
            How quickly does other nodes
            detect a disappearing node

        ● Protocol overhead:
            Ratio of total network bytes sent vs useful
            information received during discovery and description processes
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

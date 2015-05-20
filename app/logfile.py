from datetime import datetime

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
    def __init__(self, file_path, append=False):

        # output file
        if file_path:
            if append:
                self.file = open(file_path, 'a')
            else:
                self.file = open(file_path, 'w')
        else:
            self.file = None
        self.node_discovery_times = {}
        self.node_initialization_time = None

    def log(self, message):

        if self.file:
            tmp = str(datetime.now()) + " " + message + "\n"
            self.file.write(tmp)
            self.file.flush()

    def node_discovery(self, name, timestamp):
        """

        """
        if self.file:
            if not self.node_discovery_times.get(name):
                self.node_discovery_times[name] = timestamp
                self.log("Peer {0} discovered ({1})".format(name, timestamp))

    def write_summary(self):
        """
        Calculate network discovery time
        """
        if self.file:
            nw_discovery_time = 0
            for d_time in self.node_discovery_times:
                nw_discovery_time += d_time
            node_discovery_time = nw_discovery_time/len(self.node_discovery_times)

            tmp = str("\n\nSummary:\nNetwork Discovery Time: {0}\nNode Discovery Time: {1}\n".format(nw_discovery_time, node_discovery_time))
            self.file.write(tmp)
            self.file.flush()

    @staticmethod
    def log_message(filename, message):
        tmp = str(datetime.now()) + ": " + message
        #filename = "logs/" + filename
        with open(filename, 'a') as f:
            f.write(tmp)
            f.flush()
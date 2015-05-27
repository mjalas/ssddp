from printers.printer import Printer


class NodePrinter(Printer):
    """
    Printer for SSDDP nodes.
    """

    def __init__(self, node_name, log_file, print_to_ui=False):
        super().__init__(log_file, print_to_ui)
        self.node_name = node_name

    def log(self, message):
        message = self.node_name + ": " + message
        super().log(message)

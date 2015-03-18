import logging
import threading


class CommandHandler(threading.Thread):
    """

    """
    def __init__(self, command, self_node):
        threading.Thread.__init__(self)
        self._target = self.handle_command
        self.command = command
        self.logger = logging.getLogger(self_node.name + ": " + __name__)
        self.logger.info("Discovery Listener initialized")

    def handle_command(self):
        self.logger.info("Received command: " + self.command)

    def run(self):
        # self._target()
        self.handle_command()
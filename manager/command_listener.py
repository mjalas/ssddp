import threading


class CommandListener(threading.Thread):
    """

    """
    def __init__(self, command):
        self._target = self.handle_command
        self.command = command
        threading.Thread.__init__()

    def handle_command(self):
        pass

    def run(self):
        self._target()
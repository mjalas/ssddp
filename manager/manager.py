from abc import ABCMeta, abstractmethod


class Manager(metaclass=ABCMeta):
    """

    """
    @abstractmethod
    def handle_message(self):
        pass

    @abstractmethod
    def send_message(self):
        pass
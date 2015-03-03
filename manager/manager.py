from abc import ABCMeta, abstractmethod


class Manager(metaclass=ABCMeta):
    """

    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def parse_message(self, message):
        """
        Handle input message.
        :return:
        """
        return

    @abstractmethod
    def create_message(self, address):
        """
        Send message to given address.
        :return:
        """
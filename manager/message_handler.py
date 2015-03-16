from abc import ABCMeta, abstractmethod


class MessageHandler(object):
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
    def create_message(self, node):
        """
        Send message to given address.
        :return:
        """
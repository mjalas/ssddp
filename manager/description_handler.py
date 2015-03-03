from manager.description_manager import DescriptionManager
from message.description_request_list import DescriptionRequestList

class DescriptionHandler(object):
    """

    """
    def __init__(self, desciption_manager):
        if not isinstance(desciption_manager, DescriptionManager):
            raise RuntimeError
        self.description_manager = desciption_manager

    def handle_description(self, tcp_socket, description_request_list):
        """

        :return:
        """
        if not isinstance(description_request_list, DescriptionRequestList):
            raise RuntimeError
        # TODO: Continue implementing method!!
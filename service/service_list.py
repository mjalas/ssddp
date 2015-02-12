import service.service


class ServiceList(object):
    # TODO: add documentation
    """

    """
    def __init__(self):
        self.services = []

    def clear(self):
        self.services.clear()

    def add(self, new_service):
        if isinstance(new_service, service):  # TODO: need to be tested -> create unit test
            self.services.append(new_service)
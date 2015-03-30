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

    def to_list(self):
        service_list = []
        for a_service in self.services:
            service_list.append(a_service.to_json())
        return service_list

    def from_file(self, file_path):
        json_file = open(file_path)
        # TODO: fill services with contents

    def __str__(self):
        return self.to_list()
import json
import service.service
from service.service import Service


class ServiceList(object):
    # TODO: add documentation
    """

    """
    def __init__(self):
        self.services = []

    def clear(self):
        self.services.clear()

    def append(self, new_service):
        if isinstance(new_service, service):  # TODO: need to be tested -> create unit test
            self.services.append(new_service)

    def to_list(self):
        service_list = []
        for a_service in self.services:
            service_list.append(a_service.to_json())
        return service_list


    def from_file(self, file_path):
        json_file = open(file_path)
        data = json.loads(json_file.read())
        for service_key in data:
            name = data[service_key]["name"]
            s_type = data[service_key]["service_type"]
            desc = data[service_key]["description"]
            new_service = Service(name, s_type, desc)
            self.services.append(new_service)

    def __iter__(self):
        for elem in self.services:
            yield elem

    def __len__(self):
        return len(self.services)


    def __str__(self):
        return self.to_list()

    def __contains__(self, item):
        for elem in self.services:
            if elem is item:
                return True
        return False
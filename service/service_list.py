import json
import logging
import service.service
from service.service import Service


class ServiceList(object):
    # TODO: add documentation
    """

    """

    def __init__(self):
        self.services = []
        self.logger = logging.getLogger(__name__)

    def clear(self):
        self.services.clear()

    def append(self, new_service):
        if isinstance(new_service, Service):  # TODO: need to be tested -> create unit test
            self.services.append(new_service)

    def to_list(self):
        service_list = []
        for a_service in self.services:
            service_list.append(a_service.to_json())
        return service_list

    def to_discovery_list(self):
        service_list = []
        for a_service in self.services:
            service_list.append(a_service.to_discovery_json())
        return service_list

    def from_dict(self, json_dict):
        for data in json_dict:
            name = data["name"]
            s_type = ""
            if data['type']:
                s_type = data["type"]
            elif data['service_type']:
                s_type = data['service_type']
            desc = None
            try:
                desc = data["description"]
            except KeyError:
                pass
            new_service = Service(name, s_type, desc)
            self.services.append(new_service)

    def from_file(self, file_path):
        json_file = open(file_path)
        data = json.loads(json_file.read())
        for service_key in data:
            name = data[service_key]["name"]
            s_type = data[service_key]["service_type"]
            desc = data[service_key]["description"]
            new_service = Service(name, s_type, desc)
            self.services.append(new_service)

    def update_merge(self, new_services):
        """
        Updates service list with new services (another ServiceList)
            1) Add old descriptions to new services without descriptions
            2) Replace old list with new
        """
        self.logger.debug("Merging service list with new services")
        preserved_descriptions = 0
        # Loop through all new services
        for new_service in new_services:
            if not new_service.description:
                # New service has no description
                for old_service in self.services:
                    if (old_service.name == new_service.name) and old_service.description:
                        new_service.description = old_service.description
                        preserved_descriptions += 1
        self.logger.debug("Updated old list (" + str(len(self.services)) + " entries) with new list (" + str(
            len(new_services)) + " entries), preserving "+str(preserved_descriptions)+" descriptions.")

        # Replace old list with new
        self.services = new_services

    def is_empty(self):
        return len(self.services) > 0

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
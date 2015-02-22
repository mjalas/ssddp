

class Service(object):

    # TODO: add documentation
    """

    """
    def __init__(self, name, service_type, description):
        self.name = name
        self.type = service_type
        self.description = description

    def to_json(self):
        return {'name': self.name, 'type': self.type, 'description': self.description}

from crm.models import Collaborator


class ClientController:
    def __init__(self, collaborator: Collaborator):
        self.collaborator = collaborator

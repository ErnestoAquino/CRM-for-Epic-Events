from crm.models import Collaborator


class ContractController:
    def __init__(self, collaborator: Collaborator):
        self.collaborator = collaborator

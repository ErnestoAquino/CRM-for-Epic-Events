from django.core.exceptions import PermissionDenied

from crm.models import Collaborator
from crm.models import Contract
from services.services_crm import ServicesCRM


class ContractController:
    def __init__(self, collaborator: Collaborator):
        self.collaborator = collaborator
        self.services = ServicesCRM()

    def get_all_contracts(self):
        if self.collaborator.has_perm("crm.view_contract"):
            return self.services.get_all_contracts()
        else:
            raise PermissionDenied("You do not have permission to view the list of contracts.")
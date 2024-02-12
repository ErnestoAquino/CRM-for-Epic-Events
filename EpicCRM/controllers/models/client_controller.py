from django.core.exceptions import PermissionDenied
from crm.models import Collaborator
from crm.models import Client
from services.services_crm import ServicesCRM


class ClientController:
    def __init__(self, collaborator: Collaborator, services: ServicesCRM):
        self.collaborator = collaborator
        self.services = services

    def get_all_clients(self):
        if self.collaborator.has_perm("crm.view_client"):
            return self.services.get_all_clients()
        else:
            raise PermissionDenied("You do not have permission to view the list of clients.")

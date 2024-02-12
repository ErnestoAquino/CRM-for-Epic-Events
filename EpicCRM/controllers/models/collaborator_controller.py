from crm.models import Collaborator
from services.services_crm import ServicesCRM


class CollaboratorController:
    def __init__(self, collaborator: Collaborator, services: ServiceCRM):
        self.collaborator = collaborator
        self.services = services

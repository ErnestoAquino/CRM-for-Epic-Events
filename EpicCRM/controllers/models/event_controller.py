from django.core.exceptions import PermissionDenied

from crm.models import Collaborator
from crm.models import Event

from services.services_crm import ServicesCRM


class EventController:
    def __init__(self, collaborator: Collaborator):
        self.collaborator = collaborator
        self.service = ServicesCRM()

    def get_all_events(self):
        if self.collaborator.has_perm("crm.view_event"):
            return self.service.get_all_events()
        else:
            raise PermissionDenied("You do not have permission to view the list of events.")

    def get_events_for_collaborator(self):
        if self.collaborator.has_perm("crm.view_event"):
            return self.service.get_events_for_collaborator(self.collaborator.id)
        else:
            raise PermissionDenied("You do not have permission to view the events.")


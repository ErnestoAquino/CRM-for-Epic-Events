from django.core.exceptions import PermissionDenied

from crm.models import Collaborator
from crm.models import Event

from services.services_crm import ServicesCRM


class EventController:
    def __init__(self, collaborator: Collaborator, services: ServicesCRM):
        self.collaborator = collaborator
        self.service = services

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

    def get_event_by_id(self, event_id) -> Event | None:
        """
        Retrieves an event by its ID if the current collaborator is its support contact.

        Args:
            event_id (int): The ID of the event to retrieve.

        Returns:
            Event if the collaborator is authorized to modify it; None if the event doesn't exist.

        Raises:
            PermissionDenied: If the collaborator is not authorized to modify the event.
        """
        event = self.service.get_event_by_id(event_id)
        if not event:
            # TODO: Capture with Sentry.
            print(f"Not event with id: {event_id} found.")
            return None
        if event.support_contact_id != self.collaborator.id:
            raise PermissionDenied("You are not authorized to modify this event.")
        return event

    def modify_event(self, event_id):
        pass

    def can_user_modify_event(self, event_id) -> True | False:
        pass
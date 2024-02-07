from crm.models import Collaborator


class EventController:
    def __init__(self, collaborator: Collaborator):
        self.collaborator = collaborator


from crm.models import Collaborator

from controllers.models.client_controller import ClientController
from controllers.models.contract_controller import ContractController
from controllers.models.event_controller import EventController
from views.roles.support_role_view_cli import SupportRoleViewCli


class SupportRoleController:
    def __init__(self, collaborator: Collaborator):
        self.collaborator = collaborator
        self.client_controller = ClientController(self.collaborator)
        self.contract_controller = ContractController(self.collaborator)
        self.event_controller = EventController(self.collaborator)
        self.view_cli = SupportRoleViewCli()

    def start(self):
        print(f"Hi! {self.collaborator.get_full_name()}")
        choice = self.view_cli.show_main_menu(collaborator=self.collaborator)

        match choice:
            case 1:
                # TODO: View the list of all clients
                pass
            case 2:
                # TODO: View the list of all contracts
                pass
            case 3:
                # TODO: View the list of all events
                pass
            case 4:
                # TODO: View your assigned events
                pass
            case 5:
                # TODO: Modify one of your assigned events
                pass
            case _:
                # TODO: Show error message to user
                pass

from django.core.exceptions import PermissionDenied

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
                self.present_list_all_clients()
            case 2:
                self.present_list_all_contracts()
            case 3:
                self.present_list_all_events()
            case 4:
                # TODO: View your assigned events
                pass
            case 5:
                # TODO: Modify one of your assigned events
                pass
            case _:
                # TODO: Show error message to user
                pass

    def present_list_all_clients(self):
        try:
            clients = self.client_controller.get_all_clients()
            self.view_cli.display_list_of_clients(clients)
        except PermissionDenied as e:
            self.view_cli.display_error_message(str(e))

    def present_list_all_contracts(self):
        try:
            contracts = self.contract_controller.get_all_contracts()
            self.view_cli.display_list_of_contracts(contracts)
        except PermissionDenied as e:
            self.view_cli.display_error_message(str(e))

    def present_list_all_events(self):
        try:
            events = self.event_controller.get_all_events()
            self.view_cli.display_list_of_events(events)
        except PermissionDenied as e:
            self.view_cli.display_error_message(str(e))

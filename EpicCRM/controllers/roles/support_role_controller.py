from django.core.exceptions import PermissionDenied

from crm.models import Collaborator

from controllers.models.client_controller import ClientController
from controllers.models.contract_controller import ContractController
from controllers.models.event_controller import EventController
from views.roles.support_role_view_cli import SupportRoleViewCli


class SupportRoleController:
    def __init__(self, collaborator: Collaborator,
                 client_controller: ClientController,
                 contract_controller: ContractController,
                 event_controller: EventController):

        self.collaborator = collaborator
        self.client_controller = client_controller
        self.contract_controller = contract_controller
        self.event_controller = event_controller
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
                self.present_events_for_collaborator()
                pass
            case 5:
                self.modify_event_of_collaborator()
                pass
            case _:
                # TODO: Show error message to user
                pass
        continue_operation = self.view_cli.ask_user_if_continue()
        if continue_operation:
            self.start()
        else:
            self.view_cli.clear_screen()
            self.view_cli.display_info_message("Thank you for using CRM Events, until next time!")

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

    def present_events_for_collaborator(self):
        try:
            events = self.event_controller.get_events_for_collaborator()
            # TODO: Write message if not events
            self.view_cli.display_list_of_events(events)
        except PermissionDenied as e:
            self.view_cli.display_error_message(str(e))

    def modify_event_of_collaborator(self):
        self.view_cli.clear_screen()

        try:
            # Try to retrieve the list of events for the collaborator
            events = self.event_controller.get_events_for_collaborator()
            self.view_cli.display_events_for_selection(events)
        except PermissionDenied as e:
            # If the collaborator does not have permission, display error message and exit.
            self.view_cli.display_error_message(str(e))
            return

        # Check if there are events assigned to the collaborator.
        if not events:
            self.view_cli.display_info_message("No events assigned to you for modification.")
            return

        # If there are events, proceed to display them and ask the user to choose one for modification.
        event_ids = [event.id for event in events]
        selected_event_id = self.view_cli.prompt_for_get_event_id(event_ids)

        # Find the selected event by the user in the retrieved event list.
        selected_event = next((event for event in events if event.id == selected_event_id), None)

        if not selected_event:
            self.view_cli.display_error_message("Selected event not found.")

        self.view_cli.clear_screen()
        self.view_cli.display_event_details(selected_event)

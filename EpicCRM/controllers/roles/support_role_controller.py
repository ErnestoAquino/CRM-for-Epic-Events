from django.core.exceptions import PermissionDenied

from crm.models import Collaborator
from crm.models import Event

from controllers.models.client_controller import ClientController
from controllers.models.contract_controller import ContractController
from controllers.models.event_controller import EventController
from views.roles.support_role_view_cli import SupportRoleViewCli


class SupportRoleController:
    def __init__(self, collaborator: Collaborator,
                 client_controller: ClientController,
                 contract_controller: ContractController,
                 event_controller: EventController,
                 view_cli: SupportRoleViewCli):

        self.collaborator = collaborator
        self.client_controller = client_controller
        self.contract_controller = contract_controller
        self.event_controller = event_controller
        self.view_cli = view_cli

    def start(self):
        self.view_cli.display_info_message(f"Hi! {self.collaborator.get_full_name()}")

        # Shows the main menu to the collaborator
        self.view_cli.show_main_menu(collaborator=self.collaborator)

        # captures their choice.
        choice = self.view_cli.get_user_menu_choice()

        match choice:
            case 1:
                # Presents the list of all clients.
                self.view_cli.clear_screen()
                self.present_list_all_clients()
            case 2:
                # Presents the list of all contracts.
                self.view_cli.clear_screen()
                self.present_list_all_contracts()
            case 3:
                # Presents the list of all events.
                self.view_cli.clear_screen()
                self.present_list_all_events()
            case 4:
                # Presents events assigned to the collaborator.
                self.view_cli.clear_screen()
                self.present_events_for_collaborator()
            case 5:
                # Initiates the modification process for an event.
                self.view_cli.clear_screen()
                self.start_modification_process()
            case 6:
                # Exits the CRM system.
                self.exit_of_crm_system()
                return
            case _:
                self.view_cli.display_error_message("Invalid option selected. Please try again.")
                self.start()

        # Asks the collaborator if they want to continue using the system.
        continue_operation = self.view_cli.ask_user_if_continue()
        if not continue_operation:
            # Exits the CRM system if the collaborator chooses not to continue.
            self.exit_of_crm_system()
            return

        # Restarts the start method to prompt the collaborator for another choice.
        self.start()

    def present_list_all_clients(self):
        try:
            # Attempts to retrieve all clients from the client controller.
            clients = self.client_controller.get_all_clients()

            # Checks if there are no clients available.
            if not clients:
                self.view_cli.display_info_message("No clients available.")
                return

            # Displays the list of clients to the user.
            self.view_cli.display_list_of_clients(clients)
        except PermissionDenied as e:
            # If the user does not have permission to view clients, display an error message.
            self.view_cli.display_error_message(str(e))

    def present_list_all_contracts(self):
        try:
            # Tries to retrieve all contracts
            contracts = self.contract_controller.get_all_contracts()

            # Checks if there are no contracts available.
            if not contracts:
                self.view_cli.display_info_message("No contracts available.")
                return

            # Displays the list of contracts to the user.
            self.view_cli.display_list_of_contracts(contracts)

        except PermissionDenied as e:
            # If the user does not have permission to view contracts, display an error message.
            self.view_cli.display_error_message(str(e))

    def present_list_all_events(self):
        try:
            # Tries to retrieve all events
            events = self.event_controller.get_all_events()

            # Checks if there are no events available.
            if not events:
                self.view_cli.display_info_message("No events available.")
                return
            # Displays the list of events to the user.
            self.view_cli.display_list_of_events(events)

        except PermissionDenied as e:
            # If the user does not have permission to view events, display an error message.
            self.view_cli.display_error_message(str(e))

    def present_events_for_collaborator(self):
        try:
            events = self.event_controller.get_events_for_collaborator()
            if not events:
                self.view_cli.display_info_message("No events assigned to you.")
            self.view_cli.display_list_events_for_collaborator(events, collaborator=self.collaborator)
        except PermissionDenied as e:
            self.view_cli.display_error_message(str(e))

    def exit_of_crm_system(self):
        self.view_cli.clear_screen()
        self.view_cli.display_info_message("Thank you for using CRM Events, until next time!")

    def get_event_for_modification(self) -> Event | None:
        self.view_cli.clear_screen()

        try:
            # Try to retrieve the list of events for the collaborator
            events = self.event_controller.get_events_for_collaborator()
            self.view_cli.display_events_for_selection(events)
        except PermissionDenied as e:
            # If the collaborator does not have permission, display error message and exit.
            self.view_cli.display_error_message(str(e))
            return None

        # Check if there are events assigned to the collaborator.
        if not events:
            self.view_cli.display_info_message("No events assigned to you for modification.")
            return None

        # If there are events, proceed to display them and ask the user to choose one for modification.
        event_ids = [event.id for event in events]
        selected_event_id = self.view_cli.prompt_for_selection_by_id(event_ids, "Event")

        # Find the selected event by the user in the retrieved event list.
        selected_event = next((event for event in events if event.id == selected_event_id), None)

        # If the selected event is not found, inform the user.
        if not selected_event:
            self.view_cli.display_error_message("Selected event not found.")
            return None

        return selected_event

    def modify_event(self, event: Event) -> None:
        # Clears the screen before proceeding.
        self.view_cli.clear_screen()

        # Displays the details of the event to be modified.
        self.view_cli.display_event_details(event)

        modifications = self.view_cli.prompt_for_event_modification()
        # Checks if no modifications were provided.
        if not modifications:
            # Informs the user that no modifications were made and exits.
            self.view_cli.display_info_message("No modifications were made.")
            return

        # Applies the modifications to the event object.
        for field, value in modifications.items():
            setattr(event, field, value)

        # Saves the modified event.
        event.save()

        # Informs the user that the event was updated successfully.
        self.view_cli.display_info_message("Event updated successfully.")

    def start_modification_process(self):
        # Obtains the event selected for modification.
        selected_event = self.get_event_for_modification()

        if not selected_event:
            self.view_cli.display_info_message("Modification process cancelled.")
            return

        # Initiates the modification process for the selected event.
        self.modify_event(selected_event)

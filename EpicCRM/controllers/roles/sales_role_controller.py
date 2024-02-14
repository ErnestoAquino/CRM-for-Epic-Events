from django.core.exceptions import ValidationError

from controllers.models.client_controller import ClientController
from controllers.models.contract_controller import ContractController
from controllers.models.event_controller import EventController

from crm.models import Collaborator
from crm.models import Client
from services.services_crm import ServicesCRM
from views.roles.sales_role_view_cli import SalesRoleViewCli


class SalesRoleController:
    def __init__(self, collaborator: Collaborator,
                 services_crm: ServicesCRM,
                 client_controller: ClientController,
                 contract_controller: ContractController,
                 event_controller: EventController,
                 view_cli: SalesRoleViewCli):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.client_controller = client_controller
        self.contract_controller = contract_controller
        self.event_controller = event_controller
        self.view_cli = view_cli

    def start(self):
        name_to_display = self.collaborator.get_full_name() or collaborator.username

        # Shows the main menu to the collaborator
        self.view_cli.show_main_menu(name_to_display)

        # captures their choice.
        user_choice = self.view_cli.get_user_menu_choice()

        match user_choice:
            case 1:
                # Create a new Client.
                self.create_new_client()
            case 2:
                #  Update client information.
                self.start_modification_client_process()
            case 3:
                # TODO: Modify/Update clients contracts.
                pass
            case 4:
                # TODO: Filter and display contracts (e.g., unsigned or not fully paid).
                pass
            case 5:
                # TODO: Create an event for a client who has signed a contract.
                pass
            case 6:
                # View the list of all clients.
                self.view_cli.clear_screen()
                self.present_list_all_clients()
            case 7:
                # View the list of all contracts.
                self.view_cli.clear_screen()
                self.present_list_all_contracts()
            case 8:
                # View the list of all events.
                self.view_cli.clear_screen()
                self.present_list_all_events()
            case 9:
                # Exit the CRM system.
                self.exit_of_crm_system()
                return

        # Asks the collaborator if they want to continue using the system.
        continue_operation = self.view_cli.ask_user_if_continue()

        if not continue_operation:
            # Exits the CRM system if the collaborator chooses not to continue.
            self.exit_of_crm_system()
            return

        # Restarts the start method to prompt the collaborator for another choice.
        self.start()

    # ================== 1 - Create a new client.    =======================
    def create_new_client(self):
        self.view_cli.clear_screen()
        if not self.collaborator.has_perm("crm.add_client"):
            self.view_cli.display_error_message("You do not have permission to add a new client.")
        client_data = self.view_cli.get_data_for_add_new_client()
        client_data['sales_contact'] = self.collaborator

        try:
            new_client = self.services_crm.create_client(**client_data)
            self.view_cli.clear_screen()
            self.view_cli.display_info_message(f"Client {new_client.full_name} created successfully.")
            self.view_cli.display_client_details(new_client)
        except ValidationError as e:
            self.view_cli.display_error_message(str(e))
        except Exception as e:
            self.view_cli.display_error_message(f"An unexpected error occurred: {e}")

    # ================== 2 - Update client information.    =================
    def start_modification_client_process(self):
        selected_client = self.get_client_for_modification()
        if not selected_client:
            self.view_cli.display_warning_message("Modification process cancelled.")
            return
        self.modify_client(selected_client)

    def get_client_for_modification(self) -> Client | None:
        self.view_cli.clear_screen()

        if not self.collaborator.has_perm("crm.view_client"):
            self.view_cli.display_error_message("You do not have permission to view the clients")
            return None

        try:
            clients = self.services_crm.get_clients_for_collaborator(self.collaborator.id)
            self.view_cli.display_clients_for_selection(clients)
        except Exception as e:
            self.view_cli.display_error_message(f"An unexpected error occurred: {e}")
            return None

        if not clients:
            self.view_cli.display_info_message(f"No clients assigned to you.")
            return None

        clients_id = [client.id for client in clients]
        selected_client_id = self.view_cli.prompt_for_selection_by_id(clients_id, "Client")

        selected_client = next((client for client in clients if client.id == selected_client_id), None)

        if not selected_client:
            self.view_cli.display_error_message("Selected client not found.")
            return None

        return selected_client

    def modify_client(self, client: Client) -> None:
        # Clears the screen before proceeding.
        self.view_cli.clear_screen()

        # Displays the details of the client to be modified.
        self.view_cli.display_client_details(client)
        modifications = self.view_cli.prompt_for_client_modification()

        # Checks if no modifications were provided.
        if not modifications:
            # Informs the user that no modifications were made and exits.
            self.view_cli.display_info_message("No modifications were made.")
            return

        # Applies the modifications to the client object.
        for field, value in modifications.items():
            setattr(client, field, value)

        # Saves the modified client.
        client.save()

        # Informs the client was updated successfully.
        self.view_cli.display_info_message("Client updated successfully.")

    # ================== 6 - View the list of all clients.   ===============
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

    # ================== 7 - View the list of all contracts. ===============
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

    # ================== 8 - View the list of all events. ==================
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

    # ================== 9 - Exit the CRM system.         ==================
    def exit_of_crm_system(self):
        self.view_cli.clear_screen()
        self.view_cli.display_info_message("Thank you for using CRM Events, until next time!")

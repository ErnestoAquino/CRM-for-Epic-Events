from django.db import IntegrityError
from django.db import DatabaseError
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from sentry_sdk import capture_message
from typing import List
from typing import Optional

from crm.models import Collaborator
from crm.models import Client
from crm.models import Contract
from crm.models import Event
from services.services_crm import ServicesCRM
from views.roles.sales_role_view_cli import SalesRoleViewCli


class SalesRoleController:
    def __init__(self, collaborator: Collaborator,
                 services_crm: ServicesCRM,
                 view_cli: SalesRoleViewCli):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli

    def start(self):
        """
        Starts the CRM system and displays the main menu to the collaborator.

        This method displays the main menu options to the collaborator and captures their choice.
        It then performs the corresponding action based on the selected choice. After completing
        the action, it prompts the collaborator if they want to continue using the system.
        """
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
                self.process_client_modification()
            case 3:
                # Modify/Update clients contracts.
                self.process_contract_modification()
            case 4:
                # Filter and display contracts (e.g., unsigned or not fully paid).
                self.filter_contracts()
            case 5:
                # Create an event for a client who has signed a contract.
                self.process_event_creation()
            case 6:
                # View the list of all clients.
                self.show_all_clients()
            case 7:
                # View the list of all contracts.
                self.show_all_contracts()
            case 8:
                # View the list of all events.
                self.show_all_events()
            case 9:
                # Exit the CRM system.
                self.exit_of_crm_system()
                return
            case _:
                capture_message(
                    f"Invalid menu option selected: {choice}. in start() - sales controller."
                    f"Expected options were between 1 and 9",
                    level='error')
                self.view_cli.display_error_message("Invalid option selected. Please try again.")

        # Asks the collaborator if they want to continue using the system.
        continue_operation = self.view_cli.ask_user_if_continue()

        if not continue_operation:
            # Exits the CRM system if the collaborator chooses not to continue.
            self.exit_of_crm_system()
            return

        # Restarts the start method to prompt the collaborator for another choice.
        self.start()

# ====================== 1 - Create a new client.    ===================================================================
    def create_new_client(self) -> None:
        """
        Handles the creation of a new client in the CRM system.

        This method checks if the collaborator has permission to add a new client.
        Retrieves data for the new client from the view, assigns the sales contact to the new client,
        attempts to create the new client using the CRM service, and displays appropriate success or
        error messages.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Check if the collaborator has permission to add a new client.
        if not self.collaborator.has_perm("crm.add_client"):
            # Log an unauthorized access attempt.
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to create new client", level="info")
            # Display error message and return if permission is not granted.
            self.view_cli.display_error_message("You do not have permission to add a new client.")
            return

        # Get data for the new client
        client_data = self.view_cli.get_data_for_add_new_client()
        # Assign the sales contact to the new client.
        client_data['sales_contact'] = self.collaborator

        try:
            # Attempt to create the new client
            new_client = self.services_crm.create_client(**client_data)
            self.view_cli.clear_screen()

            # Display success message and client details.
            self.view_cli.display_info_message(f"Client {new_client.full_name} created successfully.")
            self.view_cli.display_client_details(new_client)
        except ValidationError as e:
            self.view_cli.display_error_message(f"Validation error: {e}")
        except DatabaseError:
            self.view_cli.display_error_message(f"I encountered a problem with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))

# ======================= 2 - Update client information.    ============================================================
    def process_client_modification(self) -> None:
        """
        Process the modification of a client.

        This method retrieves the list of clients assigned to the current collaborator,
        prompts the user to select a client for modification, and then initiates the modification
        process for the selected client.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Retrieve the clients assigned to the current collaborator.
        clients = self.get_clients_for_collaborator(self.collaborator)
        if not clients:
            return

        # Select client for modification
        selected_client_for_modification = self.select_client_from(clients)
        if not selected_client_for_modification:
            return

        self.modify_client(selected_client_for_modification)

    def get_clients_for_collaborator(self, collaborator: Collaborator) -> List[Client]:
        """
        Retrieve the list of clients assigned to a specific collaborator.

        Args:
            collaborator (Collaborator): The collaborator for whom to retrieve the clients.

        Returns:
            List[Client]: The list of clients assigned to the collaborator.

        """
        try:
            # Attempt to retrieve clients associated with the given collaborator.
            clients = self.services_crm.get_clients_for_collaborator(collaborator.id)
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(str(e))
            return []

        if not clients:
            # Display a message if there are no clients available.
            self.view_cli.display_info_message("There are no clients available to display.")

        # Return the list of clients.
        return clients

    def select_client_from(self, list_of_clients: List[Client]) -> Optional[Client]:
        """
        Prompt the user to select a client from a list of clients.

        Args:
            list_of_clients (List[Client]): List of clients to choose from.

        Returns:
            Optional[Client]: The selected client, or None if not found.

        """
        self.view_cli.clear_screen()

        # Display the list of clients for selection
        self.view_cli.display_clients_for_selection(list_of_clients)

        # Retrieve the IDs of all collaborators in the list.
        clients_ids = [client.id for client in list_of_clients]

        # Prompt the user to select a client by ID.
        selected_client_id = self.view_cli.prompt_for_selection_by_id(clients_ids, "Client")

        # Find the selected client from the list
        selected_client = next((client for client in list_of_clients if client.id == selected_client_id), None)

        if not selected_client:
            # If the select client is not found, display an error message
            self.view_cli.display_error_message("We couldn't find the client. Please try again later.")

        # Return the selected client
        return selected_client

    def modify_client(self, client: Client) -> None:
        """
        Modify a client.

        This method displays the details of the client to be modified,
        prompts the user for modifications, and attempts to modify the client using the provided data.

        Args:
            client (Client): The client to be modified.

        Returns:
            None
        """
        # Clears the screen before proceeding.
        self.view_cli.clear_screen()

        # Displays the details of the client to be modified.
        self.view_cli.display_client_details(client)
        modifications = self.view_cli.get_data_for_client_modification()

        # Checks if no modifications were provided.
        if not modifications:
            # Informs the user that no modifications were made and exits.
            self.view_cli.display_info_message("No modifications were made.")
            return

        try:
            # Attempts to modify the client using the provided data
            client_modified = self.services_crm.modify_client(client, modifications)
            self.view_cli.clear_screen()
            self.view_cli.display_client_details(client_modified)
            self.view_cli.display_info_message("The client has been modified successfully.")
        except ValidationError as e:
            self.view_cli.display_error_message(str(e))
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))

# ====================== 3 - Modify/Update clients contracts.   ========================================================
    def process_contract_modification(self) -> None:
        """
        Process the modification of a contract by a collaborator.

        This method retrieves contracts assigned to the current collaborator,
        prompts the user to select a contract from the list, and then initiates
        the modification process for the selected contract.

        Returns:
            None
        """
        contracts = self.get_contracts_assigned_to(self.collaborator.id)
        if not contracts:
            return

        selected_contract = self.select_contract_form(contracts)
        if not selected_contract:
            return

        self.modify_contract(selected_contract)

    def get_contracts_assigned_to(self, collaborator_id: int, filter_type: str = None) -> List[Contract]:
        """
        Retrieve contracts assigned to a specific collaborator, optionally filtered by type.

        Args:
            collaborator_id (int): The ID of the collaborator whose contracts are to be retrieved.
            filter_type (str, optional): The type of filter to be applied to the contracts.
                Possible values are:
                    - "signed": Filters contracts that are signed.
                    - "not_signed": Filters contracts that are not signed.
                    - "no_fully_paid": Filters contracts that are not fully paid yet.
                    - None: No additional filtering.
                Defaults to None.

        Returns:
            List[Contract]: A list of contracts assigned to the collaborator, optionally filtered.
        """
        try:
            # Retrieve contracts assigned to the collaborator
            contracts = self.services_crm.get_filtered_contracts_for_collaborator(collaborator_id, filter_type)
        except ValueError as e:
            self.view_cli.display_error_message(str(e))
            return []
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(str(e))
            return []

        if not contracts:
            # Display a message if there are no contracts available to display.
            self.view_cli.display_info_message("There are no contracts to display")

        return contracts

    def select_contract_form(self, list_of_contracts: List[Contract]) -> Optional[Contract]:
        """
        Prompt the user to select a contract from a list of contracts.

        Args:
            list_of_contracts (List[Contract]): A list of contracts to choose from.

        Returns:
            Optional[Contract]: The selected contract, or None if no contract is selected or found.
        """
        self.view_cli.clear_screen()
        self.view_cli.display_contracts_for_selection(list_of_contracts)

        # Create list with contract ids available
        contracts_ids = [contract.id for contract in list_of_contracts]

        # Prompt user to select a contract by ID
        selected_contract_id = self.view_cli.prompt_for_selection_by_id(contracts_ids, "Contract")

        # Find the select contract by ID
        selected_contract = next((contract for contract in list_of_contracts if contract.id == selected_contract_id),
                                 None)

        # If the contract is not found, display error message
        if not selected_contract:
            self.view_cli.display_error_message("We couldn't find the contract. Please try again later.")

        return selected_contract

    def modify_contract(self, contract: Contract) -> None:
        self.view_cli.clear_screen()

        # Displays the details of the event to be modified.
        self.view_cli.display_contract_details(contract)

        modifications = self.view_cli.get_data_for_contract_modification()

        # Checks if no modifications were provided.
        if not modifications:
            # Informs the user that no modifications were made and exits.
            self.view_cli.display_info_message("No modifications were made.")
            return

        try:
            contract_modified = self.services_crm.modify_contract(contract, modifications)
            self.view_cli.clear_screen()

            # Display the details of the modified contract
            self.view_cli.display_contract_details(contract_modified)

            # Inform the user tht the contract has been modifies successfully
            self.view_cli.display_info_message("The contract has been modified successfully.")
            return
        except ValidationError as e:
            self.view_cli.display_error_message(str(e))
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))

# ====================== 4 - Filter clients contracts.       ===========================================================
    def filter_contracts(self):
        """
        Filter and display contracts based on the collaborator's choice.

        This method prompts the collaborator to select a filter option for contracts,
        retrieves the filtered contracts based on the selected filter type,
        and displays the list of filtered contracts.

        Returns:
            None
        """

        filter_types = {
            1: None,  # No additional filter, get all contracts
            2: "no_fully_paid",
            3: "not_signed",
        }
        # Prompt the collaborator to select a filter option.
        choice = self.view_cli.get_contract_filter_choices()

        self.view_cli.clear_screen()

        # Check if the choice is valid.
        if choice not in filter_types:
            self.view_cli.display_error_message("Invalid choice. Please try again.")
            return

        # Retrieve the filter type based on the collaborator's choice.
        filter_type = filter_types[choice]

        # Retrieve contracts assigned to the collaborator with the specified filter.
        contracts_to_display = self.get_contracts_assigned_to(self.collaborator.id, filter_type)

        if not contracts_to_display:
            return

        # Display the list of filtered contracts.
        self.view_cli.display_list_of_contracts(contracts_to_display)

# ====================== 5 - Create an event for a client who has signed a contract   ==================================
    def process_event_creation(self) -> None:
        """
        Process the creation of an event associated with a signed contract.

        This method clears the screen, retrieves signed contracts assigned to the
        current collaborator, prompts the user to select a contract from the list,
        and then initiates the event creation process for the selected contract.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Retrieve signed contracts assigned to the current collaborator.
        signed_contracts = self.get_contracts_assigned_to(self.collaborator.id, filter_type="signed")
        if not signed_contracts:
            return

        # Prompt the user to select a signed contract from the list.
        selected_contract = self.select_contract_from_list(signed_contracts)
        if not selected_contract:
            return

        # Initiate the event creation for the selected contract.
        self.create_event_for_signed_contract(selected_contract)

    def create_event_for_signed_contract(self, signed_contract: Contract) -> None:
        """
        Create an event associated with a signed contract.

        This method displays details of the signed contract,
        prompts the user to provide information for the new event, and then creates
        the event using the provided data.

        Args:
            signed_contract (Contract): The signed contract associated with the event.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Display details of the signed contract.
        self.view_cli.display_contract_details(signed_contract)
        event_data = self.view_cli.get_data_for_add_new_event()

        # Associate the signed contract with the event data.
        event_data["contract"] = signed_contract

        try:
            # Create the event using the provided data.
            new_event = self.services_crm.create_event(**event_data)
            self.view_cli.display_event_details(new_event)
            self.view_cli.display_info_message("Event created successfully.")
        except ValidationError as e:
            self.view_cli.display_error_message(f"Validation error: {e}")
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))

    def select_contract_from_list(self, filtered_contracts: List[Contract]) -> Optional[Contract]:
        """
        Prompt the user to select a contract from a list for further action.

        This method clears the screen, displays a list of contracts for selection,
        prompts the user to choose a contract by its ID, and returns the selected contract.

        Args:
            filtered_contracts (List[Contract]): The list of contracts to choose from.

        Returns:
            Optional[Contract]: The selected contract, or None if not found.
        """
        self.view_cli.clear_screen()

        # Display list of contracts for user selection
        self.view_cli.display_contracts_for_selection(filtered_contracts)

        # Create list of ids contracts
        contracts_ids = [contract.id for contract in filtered_contracts]

        # Prompt the user to select a contract for add new event
        selected_contract_id = self.view_cli.prompt_for_selection_by_id(contracts_ids, "Contract")

        # Find the selected contract from the list based on the ID selected
        selected_contract = next((contract for contract in filtered_contracts if contract.id == selected_contract_id),
                                 None)

        if not selected_contract:
            # If the selected contract is not found
            self.view_cli.display_error_message("We could not find the selected contract. Please try again.")

        return selected_contract

# ====================== 6 - View the list of all clients.   ===========================================================
    def show_all_clients(self) -> None:
        """
        Displays the list of all clients.

        This method first checks if the current collaborator has permission to view the client list.
        If permission is granted, it retrieves the list of all clients and displays them.
        If no clients are found or if the collaborator does not have permission, it returns.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Check if the collaborator has permission to view clients.
        if not self.collaborator.has_perm("crm.view_client"):
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to the list of clients", level="info")
            self.display_info_message("You do not have permission to view the list of clients.")
            return

        # Retrieve the list of all clients.
        clients = self.get_all_clients()

        # If no clients are found, return
        if not clients:
            return

        # Display the list of clients.
        self.view_cli.display_list_of_clients(clients)

    def get_all_clients(self) -> List[Client]:
        """
        Retrieves all clients from the CRM service.

        This method attempts to retrieve all clients from the CRM service.
        It handles potential database errors and returns an empty list if no clients are found.

        Returns:
            List[Client]: A list of client objects retrieved from the CRM service.
        """

        try:
            # Attempt to retrieve all clients
            clients = self.services_crm.get_all_clients()
        except DatabaseError:
            self.view_cli.display_error_message("I encountered an error with the database. Please try again.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(f"{e}")
            return []

        # If no clients are retrieved, display message
        if not clients:
            self.view_cli.display_info_message("No customers currently available to display.")

        return clients

# ====================== 7 - View the list of all contracts. ===========================================================
    def show_all_contracts(self) -> None:
        """
        Displays the list of all contracts.

        This method checks if the current collaborator has permission to view the list of contracts.
        If permission is granted, it retrieves the list of all contracts
        and displays them. If no contracts are found or if the collaborator does not have permission,
        it returns without displaying anything.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Check if the collaborator has permission to view contracts
        if not self.collaborator.has_perm("crm.view_contract"):
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to the list of contract", level="info")
            self.view_cli.display_info_message("You do not have permission to view the list of contracts.")

        # Retrieve the list of all contracts
        contracts = self.get_all_contracts()

        # If not contracts are found, return
        if not contracts:
            return

        # Display the list of contracts
        self.view_cli.display_list_of_contracts(contracts)

    def get_all_contracts(self) -> List[Contract]:
        """
        Retrieves all contracts from the CRM service.

        Returns:
            List[Contract]: A list of contracts objects retrieved from the CRM service.
        """

        try:
            # Attempt to retrieve all contracts
            contracts = self.services_crm.get_all_contracts()
        except DatabaseError:
            self.view_cli.display_error_message("I encountered an error with the database. Please try again.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(f"{e}")
            return []

        # If no contracts are retrieved, display message
        if not contracts:
            self.view_cli.display_info_message("No customers currently available to display.")

        return contracts

# ======================= 8 - View the list of all events. =============================================================
    def show_all_events(self) -> None:
        """
        Displays the list of all events.

        This method first checks if the current collaborator has permission to view the list of events.
        If permission is granted, it retrieves the list of all events and displays them.
        If no events are found or if the collaborator does not have permission,
        it returns without displaying anything.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Check if the collaborator has permission to view events
        if not self.collaborator.has_perm("crm.view_event"):
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to the list of events", level="info")
            self.view_cli.display_info_message("You do not have permission to view the list of events.")

        # Retrieve the list of all events
        events = self.get_events_with_optional_filter()

        # If not events are found, return
        if not events:
            return

        # Display the list of events
        self.view_cli.display_list_of_events(events)

    def get_events_with_optional_filter(self, support_contact_required: Optional[bool] = None) -> List[Event]:
        """
        Retrieves events from the CRM service with an optional support contact filter.
        Handles potential database errors and returns an empty list if no events are found.
        Args:
            support_contact_required (Optional[bool]): Flag indicating if events with support
            contact requirement should be filtered. Defaults to None.
        Returns:
            List[Event]: A list of event objects retrieved from the CRM service.
        """
        try:
            # Retrieve events from the CRM service with an optional support contact filter.
            events = self.services_crm.get_all_events_with_optional_filter(support_contact_required)
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(f"{e}")
            return []

        # Display a message if there are no events available.
        if not events:
            self.view_cli.display_info_message("There are no events available to display.")

        # Return the list of events.
        return events

# ====================== 9 - Exit the CRM system.         ==============================================================
    def exit_of_crm_system(self):
        self.view_cli.clear_screen()
        self.view_cli.display_info_message("Thank you for using CRM Events, until next time!")

from typing import Optional
from typing import List
from sentry_sdk import capture_message
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.db.models.query import QuerySet
from crm.models import Collaborator
from crm.models import Client
from crm.models import Contract
from crm.models import Event
from services.services_crm import ServicesCRM
from views.roles.management_role_view_cli import ManagementRoleViewCli


class ManagementRoleController:
    MAIN_MENU_OPTIONS = [
        "1 - Create, update, and delete collaborators in the CRM system.",
        "2 - Create and modify all contracts.",
        "3 - Filter and display events, for example, show all events without an assigned 'support' contact.",
        "4 - Assign or change the 'support' collaborator associated with an event.",
        "5 - View the list of all clients.",
        "6 - View the list of all contracts.",
        "7 - View the list of all events.",
        "8 - Exit the CRM system."
    ]

    SUB_MENU_MANAGE_COLLABORATORS = [
        "1 - Create  a collaborator in the CRM system.",
        "2 - Update a collaborator in the CRM system.",
        "3 - Delete a collaborator in the CRM system",
        "4 - Return to main menu"
    ]

    SUB_MENU_MANAGE_CONTRACTS = [
        "1 - Create new contract.",
        "2 - Update a contract.",
        "3 - Return to main menu"
    ]

    SUB_MENU_EVENTS = [
        "1 - View events with support contact assigned.",
        "2 - View events without support contact assigned.",
        "3 - Return to main menu"
    ]

    def __init__(self, collaborator: Collaborator,
                 services_crm: ServicesCRM,
                 view_cli: ManagementRoleViewCli):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli

    def start(self) -> None:
        """
        Starts the CRM system and displays the main menu to the collaborator.

        This method displays the main menu options to the collaborator and captures their choice.
        It then performs the corresponding action based on the selected choice. After completing
        the action, it prompts the collaborator if they want to continue using the system.
        """
        name_to_display = self.collaborator.get_full_name() or collaborator.username

        # Shows the main menu to the collaborator
        self.view_cli.show_menu(name_to_display, self.MAIN_MENU_OPTIONS)

        # captures their choice.
        choice = self.view_cli.get_collaborator_choice(limit=len(self.MAIN_MENU_OPTIONS))

        match choice:
            case 1:
                # Create, update, and delete collaborators in the CRM system.
                self.manage_collaborators()
            case 2:
                # Create and modify all contracts.
                self.manage_contract()
            case 3:
                # Show all events without an assigned 'support' contact.
                self.manage_events()
            case 4:
                # Assign or change the 'support' collaborator associated with an event.
                self.process_modify_support_contact_in_event()
            case 5:
                # View the list of all clients.
                self.show_all_clients()
            case 6:
                # View the list of all contracts.
                self.show_all_contracts()
            case 7:
                # View the list of all events.
                self.show_all_events()
            case 8:
                #  Exit the CRM system.
                self.exit_of_crm_system()
                return
            case _:
                capture_message(
                    f"Invalid menu option selected: {choice}. in start() - management controller."
                    f"Expected options were between 1 and {len(self.MAIN_MENU_OPTIONS)}.",
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

# ================================== 1 - Manage Collaborators.   =======================================================
    def manage_collaborators(self) -> None:
        """
        Manages collaborators by providing options for creating, updating, and deleting collaborators.

        This method displays a menu for managing collaborators. The menu options include creating, updating,
        and deleting collaborators, as well as returning to the main menu. The method captures the user's choice
        and performs the corresponding action.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Check if the collaborator has the "manage_collaborator" permission which allows CRUD operations on
        # collaborators.
        if not self.collaborator.has_perm("crm.manage_collaborators"):
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to manage collaborators", level="info")
            self.view_cli.display_error_message("You do not have permission to manage collaborators.")
            return

        # Shows the submenu for manage collaborators
        self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_MANAGE_COLLABORATORS)

        # captures their choice.
        choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_MANAGE_COLLABORATORS))

        match choice:
            case 1:
                # Create  a collaborator in the CRM system
                self.process_collaborator_creation()
            case 2:
                #  Update a collaborator in the CRM system
                self.process_collaborator_modification()
            case 3:
                #  Delete a collaborator in the CRM system
                self.process_collaborator_removal()
            case 4:
                # Return to the main menu
                self.start()
            case _:
                capture_message(
                    f"Invalid menu option selected: {choice}. in manage_collaborators() - management controller."
                    f"Expected options were between 1 and {len(self.SUB_MENU_MANAGE_COLLABORATORS)}.",
                    level='error')
                self.view_cli.display_info_message("Invalid option selected. Please try again.")
                return

    def process_collaborator_creation(self) -> None:
        """
        Handles the process of creating a new collaborator.

        Continuously prompts the user to enter data for creating a new collaborator until successful registration
        or the user decides to stop.

        Returns:
            None
        """
        while True:
            self.view_cli.clear_screen()
            self.view_cli.display_info_message("Registering new collaborator...")

            # Prompt the user to provide data for creating a new collaborator.
            data_collaborator = self.view_cli.get_data_for_create_collaborator()

            try:
                # Attempt to register the new collaborator with the provided data.
                collaborator = self.services_crm.register_collaborator(**data_collaborator)

                # If registration is successful, display the details of the newly registered collaborator.
                self.view_cli.clear_screen()
                self.view_cli.display_collaborator_details(collaborator)
                self.view_cli.display_info_message("User registered successfully!")

                # Exit the loop.
                break
            except ValidationError as e:
                self.view_cli.display_error_message(str(e))

                # Ask the user if they want to try again.
                continue_operation = self.view_cli.get_user_confirmation("Do you want try again?")

                # If the user chooses not to continue, exit the loop.
                if not continue_operation:
                    break
            except DatabaseError:
                self.view_cli.display_error_message("I encountered a problem with the database. Please try again.")
            except Exception as e:
                self.view_cli.display_error_message(str(e))
                break

    def process_collaborator_modification(self) -> None:
        """
        Handles the process of modifying a collaborator.

        Retrieves a list of all collaborators.
        If there are no collaborators, exits the function.
        Otherwise, prompts the user to select a collaborator.
        Initiates the modification process for the selected collaborator.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Retrieve a list of all collaborators.
        collaborators = self.get_all_collaborators()

        # If there are no collaborators, exit the function.
        if not collaborators:
            return

        # Prompt the user to select a collaborator.
        selected_collaborator = self.select_collaborator_from(collaborators)

        # If no collaborator is selected, exit the function.
        if not selected_collaborator:
            return

        # Initiate the modification process for the selected collaborator.
        self.modify_collaborator(selected_collaborator)

    def select_collaborator_from(self, list_of_collaborators: List[Collaborator],
                                 message: Optional[str] = None) -> Optional[Collaborator]:
        """
        Selects a collaborator from the given list of collaborators.

        Clears the screen and displays the list of collaborators for selection.
        Retrieve the IDs of all collaborators in the list.
        Prompts the user to select a collaborator by ID.
        Returns the selected collaborator from the list, if found.

        Args:
            list_of_collaborators (List[Collaborator]): The list of collaborators to choose from.
            message (Optional[str]): An optional message to display before the selection. Default is None.
        Returns:
            Optional[Collaborator]: The selected collaborator, or None if not found.
        """
        self.view_cli.clear_screen()

        # Display the list of collaborators for user selection.
        self.view_cli.display_collaborators_for_selection(list_of_collaborators)

        if message:
            self.view_cli.display_info_message(message)

        # Retrieve the IDs of all collaborators in the list.
        collaborators_ids = [collaborator.id for collaborator in list_of_collaborators]

        # Prompt the user to select a collaborator by ID.
        selected_collaborator_id = self.view_cli.prompt_for_selection_by_id(collaborators_ids, "Collaborator")

        # Find the selected collaborator from the list based on the ID.
        selected_collaborator = next((collaborator for collaborator in list_of_collaborators
                                      if collaborator.id == selected_collaborator_id), None)

        if not selected_collaborator:
            # If the selected collaborator is not found, display an error message.
            self.view_cli.display_error_message("We couldn't find the collaborator. Please try again later.")

        # Return the selected collaborator.
        return selected_collaborator

    def get_all_collaborators(self) -> List[Collaborator]:
        """
        Retrieves all collaborators from the CRM service.

        Tries to retrieve all collaborators from the CRM service.
        If a database error occurs during retrieval, it displays an error message,
        and returns an empty list.
        If any other unexpected exception occurs, it displays an error message,
        and returns an empty list.
        If it finds no collaborators, it displays an information message.
        Finally, it returns the list of collaborators.

        Returns:
            List[Collaborator]: A list of all collaborators retrieved from the CRM service.
        """
        try:
            collaborators = self.services_crm.get_all_non_superuser_collaborators()
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(f"{e}")
            return []

        if not collaborators:
            # Display an information message if no collaborators are found.
            self.view_cli.display_info_message("There are no collaborators available to display.")

        return collaborators

    def modify_collaborator(self, selected_collaborator: Collaborator) -> None:
        """
        Modifies a collaborator.

        Displays the details of the selected collaborator and prompts the user to enter modifications.
        If no modifications are made, the function informs the user and returns.
        Otherwise, it attempts to modify the collaborator using the provided data.
        If a validation error occurs, the error message is displayed and the user is prompted to try again.

        Args:
            selected_collaborator (Collaborator): The collaborator to be modified.

        Returns:
            None
        """
        while True:
            # Display the details of the selected collaborator.
            self.view_cli.display_collaborator_details(selected_collaborator)

            # Get collaborator data for modification from the user.
            collaborator_data = self.view_cli.get_data_for_modify_collaborator(selected_collaborator.get_full_name())

            if not collaborator_data:
                # If no modifications were made, inform the user and return.
                self.view_cli.display_info_message("No modifications were made.")
                return

            try:
                # Attempt to modify the collaborator using the provided data.
                collaborator_modified = self.services_crm.modify_collaborator(selected_collaborator, collaborator_data)
                self.view_cli.clear_screen()
                self.view_cli.display_collaborator_details(collaborator_modified)
                self.view_cli.display_info_message("The collaborator has been modified successfully.")
                break
            except ValidationError as e:
                # Display validation error and prompt for continuation
                self.view_cli.display_error_message(str(e))
                continue_operation = self.view_cli.get_user_confirmation("Do you want to try modifying again?")
                if not continue_operation:
                    break
            except DatabaseError:
                self.view_cli.display_error_message("I encountered a problem with the database. Please try again.")
                break
            except Exception as e:
                self.view_cli.display_error_message(str(e))
                break

    def process_collaborator_removal(self) -> None:
        """
        Handles the process of removing a collaborator.

        Retrieves all collaborators, allows the user to select a collaborator to remove, and then
        deletes the selected collaborator.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Retrieve all collaborators
        collaborators = self.get_all_collaborators()
        if not collaborators:
            return

        # Select a collaborator to remove
        select_collaborator = self.select_collaborator_from(collaborators)
        if not select_collaborator:
            return

        # Delete the selected collaborator
        self.delete_collaborator(select_collaborator)

    def delete_collaborator(self, collaborator: Collaborator) -> None:
        """
        Handles the deletion of a collaborator.

        This method displays the details of the collaborator to be deleted,
        confirms with the user if they want to proceed with the deletion,
        and then attempts to delete the collaborator. It handles database
        errors and other unexpected exceptions.

        Args:
            collaborator (Collaborator): The collaborator to be deleted.

        Returns:
            None
        """
        self.view_cli.clear_screen()
        self.view_cli.display_collaborator_details(collaborator)
        self.view_cli.display_warning_message("Please note that this action is irreversible.")

        # Confirm with the user if they want to proceed with deletion
        continue_action = self.view_cli.get_user_confirmation("Do you want to delete the collaborator?")

        # If user cancels, display message and return
        if not continue_action:
            self.view_cli.display_info_message("The deletion of the collaborator has been canceled.")
            return
        try:
            # Attempt to delete the collaborator
            self.services_crm.delete_collaborator(collaborator)
            self.view_cli.display_info_message("Collaborator successfully deleted.")
        except DatabaseError:
            self.view_cli.display_error_message("A problem occurred with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(f"An unexpected error occurred: {e}")

# ================================== 2 - Manage Contracts.       =======================================================
    def manage_contract(self) -> None:
        """
        Manages the contract submenu.

        Clears the screen and checks if the collaborator has permission to manage contracts.
        If the collaborator lacks permission, an error message is displayed.
        Otherwise, the submenu for managing contracts is displayed.
        The user's choice is captured, and actions are performed accordingly,
        such as creating a contract, updating a contract, or returning to the main menu.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Check if the collaborator has the "manage_contracts_creation_modification" permission
        # which allows modification and update operations on contracts.
        if not self.collaborator.has_perm("crm.manage_contracts_creation_modification"):
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to manage_contracts", level="info")
            self.view_cli.display_error_message("You do not have permission to manage contracts.")
            return

        # Shows the submenu for manage contracts.
        self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_MANAGE_CONTRACTS)

        # captures their choice.
        choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_MANAGE_CONTRACTS))

        match choice:
            case 1:
                # Create a contract in the CRM system
                self.process_contract_creation()
            case 2:
                #  Update a contract in the CRM system
                self.process_contract_modification()
            case 3:
                # Return to the main menu
                self.start()
            case _:
                capture_message(
                    f"Invalid menu option selected: {choice}. in manage_contract() - management controller."
                    f"Expected options were between 1 and {len(self.SUB_MENU_MANAGE_CONTRACTS)}.",
                    level='error')
                self.view_cli.display_info_message("Invalid option selected. Please try again.")
                return

    def process_contract_creation(self) -> None:
        """
        Handles the process of creating a new contract.

        This method guides the user through the process of creating a new contract.
        It retrieves all clients, allows the user to select a client, and then creates
        a contract for the selected client.

        Returns:
            None
        """
        self.view_cli.clear_screen()
        # Retrieve all clients
        clients = self.get_all_clients()

        # If no clients available, return
        if not clients:
            return

        # Select a client for contract creation
        selected_client = self.select_client_from(clients)

        # If no client selected, return
        if not selected_client:
            return

        # Create a contract for the selected client
        self.create_contract_for(selected_client)

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

    def select_client_from(self, clients: List[Client]) -> Optional[Client]:
        """
        Guides the user to select a client from a list for contract assignment.

        This method displays a list of clients for the user to choose from and prompts them to select
        a client to whom they want to assign the contract they are about to create. It returns the selected
        client object or None if the selection is invalid or no client is found.

        Args:
            clients (List[Client]): A list of client objects from which the user selects.

        Returns:
            Optional[Client]: The selected client object or None if not found or selection is invalid.
        """

        self.view_cli.clear_screen()
        self.view_cli.display_clients_for_selection(clients)
        self.view_cli.display_info_message("Please select the client to whom you want to assign "
                                           "the contract you are about create.")
        # Extract client IDs for selection
        clients_ids = [client.id for client in clients]

        # Prompt user to select a client by ID
        selected_client_id = self.view_cli.prompt_for_selection_by_id(clients_ids, "Client")

        # Find the selected client by ID
        selected_client = next((client for client in clients if client.id == selected_client_id), None)

        # If no client is found, display error message
        if not selected_client:
            self.view_cli.display_error_message("We couldn't find the client. Please try again later.")

        return selected_client

    def create_contract_for(self, client: Client) -> None:
        """
        Handles the creation of a new contract for a given client.

        This method guides the user through the process of creating a new contract for a specific client.
        It displays the client details, prompts the user to enter contract data, and then creates the contract.
        It handles potential errors during contract creation and displays appropriate error messages.

        Args:
            client (Client): The client for whom the contract is being created.

        Returns:
            None
        """
        self.view_cli.clear_screen()
        self.view_cli.display_client_details(client)
        self.view_cli.display_info_message(f"You are creating a new contract for: {client.full_name}")

        # Get contract data from the user
        data_contract = self.view_cli.get_data_for_create_contract()
        data_contract["client"] = client
        data_contract["sales_contact"] = client.sales_contact

        try:
            # Create the contract using CRM service
            new_contract = self.services_crm.create_contract(**data_contract)
            self.view_cli.display_info_message("Contract created successfully.")
            self.view_cli.display_contract_details(new_contract)

        except ValidationError as e:
            # Handle validation error
            self.view_cli.display_error_message(f"Validation error: {e}")
        except DatabaseError:
            # Handle database error
            self.view_cli.display_error_message("A database error occurred. Please try again later.")
        except Exception as e:
            # Handle unexpected error
            self.view_cli.display_error_message(f"An unexpected error occurred: {e}")

    def process_contract_modification(self) -> None:
        """
        Handles the process of modifying a contract.

        Clears the screen and retrieves all contracts. If no contracts are found, the function returns early.
        Otherwise, it prompts the user to select a contract to modify and  initiates the modification
        process for the selected contract.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Retrieve all contracts.
        contracts = self.get_all_contracts()

        if not contracts:
            # If no contracts are found, return early.
            return

        # Prompt the user to select a contract to modify
        selected_contract = self.select_contract_from(contracts)

        if not selected_contract:
            # If no contract is selected, return.
            return

        # Initiate the modification process for the selected contract.
        self.modify_contract(selected_contract)

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

    def select_contract_from(self, contracts: List[Contract]) -> Optional[Contract]:
        self.view_cli.clear_screen()
        self.view_cli.display_contracts_for_selection(contracts)
        self.view_cli.display_info_message("Please select the contract you wish modify.")

        contracts_ids = [contract.id for contract in contracts]

        selected_contract_id = self.view_cli.prompt_for_selection_by_id(contracts_ids, "Contract")
        selected_contract = next((contract for contract in contracts if contract.id == selected_contract_id), None)

        if not selected_contract:
            self.view_cli.display_error_message("We couldn't find the contract. Please try again later.")

        return selected_contract

    def modify_contract(self, selected_contract: Contract) -> None:
        """
        Handles the modification of a contract.

        This method guides the user through the process of modifying a contract.
        It displays the details of the selected contract, prompts the user to enter
        modifications, and then attempts to modify the contract using the provided data.
        It handles potential errors during the modification process and displays appropriate
        error messages.

        Args:
            selected_contract (Contract): The contract to be modified.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Displays the details of the selected contract.
        self.view_cli.display_contract_details(selected_contract)

        # Gets contract data for modification from the user.
        contract_data = self.view_cli.get_data_for_modify_contract()

        if not contract_data:
            # If no modifications were made, inform the user and return.
            self.view_cli.display_info_message("No modifications were made.")
            return

        try:
            # Attempts to modify the contract using the provided data.
            contract_modified = self.services_crm.modify_contract(selected_contract, contract_data)
            self.view_cli.clear_screen()

            # Displays the details of the modified contract
            self.view_cli.display_contract_details(contract_modified)

            # Informs the user that the contract has been modified successfully.
            self.view_cli.display_info_message("The contract has been modified successfully.")
            return
        except ValidationError as e:
            self.view_cli.display_error_message(str(e))
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))

# =================================== 3 - Display  Events.   ===========================================================
    def manage_events(self):
        """
        Manages the 'events' submenu.

        Clears the screen and checks if the collaborator has permission to view events.
        If the collaborator lacks permission, an error message is displayed.
        Otherwise, the submenu for managing events is displayed.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Check if the collaborator has the "view_event" permission.
        if not self.collaborator.has_perm("crm.view_event"):
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to list of events in manage events.", level="info")
            self.view_cli.display_error_message("You do not have permission to view events.")
            return

        # Show submenu for display events
        self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_EVENTS)

        # Captures their choice
        choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_EVENTS))

        match choice:
            case 1:
                # Show events with support contact assigned
                self.show_events_with_support_contact_assigned()
                pass
            case 2:
                # Show events without support contact assigned
                self.show_events_without_support_contact_assigned()
                pass
            case 3:
                # Return to the main menu
                self.start()
            case _:
                self.view_cli.display_info_message("Invalid option selected. Please try again.")
                capture_message(
                    f"Invalid menu option selected: {choice}. "
                    f"Expected options were between 1 and {len(self.SUB_MENU_EVENTS)}.",
                    level='error')
                return

    def show_events_with_support_contact_assigned(self) -> None:
        """
        Displays events with a support contact assigned.

        Retrieves events from the CRM service, filtering out those that have
        a support contact. If no such events are found, the function returns early.
        Otherwise, it displays the list of events to the user.

        Returns:
            None
        """

        # Retrieve events with a support contact assigned.
        events_to_show = self.get_events_with_optional_filter(support_contact_required=True)

        if not events_to_show:
            # If no events are found, return early.
            return

        # Display the list of events to the user.
        self.view_cli.display_list_of_events(events_to_show)

    def show_events_without_support_contact_assigned(self) -> None:
        """
        Displays events without a support contact assigned.

        Retrieves events from the CRM service, filtering out those that do not have
        a support contact. If no such events are found, the function returns early.
        Otherwise, it displays the list of events to the user.

        Returns:
            None
        """

        # Retrieve events without a support contact assigned.
        events_to_show = self.get_events_with_optional_filter(support_contact_required=False)

        if not events_to_show:
            # If no events are found, return early
            return

        # Display the list of events to the user
        self.view_cli.display_list_of_events(events_to_show)

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

# ================================== 4 - Assign Support Contact to event.  =============================================
    def process_modify_support_contact_in_event(self) -> None:
        """
        Handles the modification of the support contact in an event.

        This method guides the user through the process of modifying the support contact in an event.
        It retrieves a list of events. If no events are found, it returns.
        Otherwise, it prompts the user to select an event from the list.
        It then retrieves a list of support collaborators, it prompts the user to select a support collaborator.
        Finally, it adds the selected support collaborator to the selected event, displays the details of the
        modified event, and informs the user that the support contact has been correctly assigned.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Retrieve a list of events
        events = self.get_events_with_optional_filter(support_contact_required=None)
        if not events:
            return

        # Prompt the user to select an event from the list.
        selected_event = self.select_event_from(events)
        if not selected_event:
            return

        # Retrieve a list of support collaborators.
        support_collaborators = self.get_support_collaborators()
        if not support_collaborators:
            return

        # Prompt the user to select a support collaborator.
        selected_support_collaborator = self.select_collaborator_from(support_collaborators,
                                                                      "Select the new support contact "
                                                                      "for the event")

        # Add the selected support collaborator to the selected event.
        event_with_new_support_collaborator = self.add_support_contact_to_event(selected_event,
                                                                                selected_support_collaborator)

        # Display the details of the modified event.
        self.view_cli.display_event_details(event_with_new_support_collaborator)

        # Inform the user that the support contact has been correctly assigned to the event.
        self.view_cli.display_info_message(f"The support contact {selected_support_collaborator.get_full_name()}"
                                           f"has been correctly assigned to the event.")

    def select_event_from(self, list_of_events: List[Event]) -> Optional[Event]:
        """
        Allows the user to select an event from a list.

        This method displays a list of events to the user for selection.
        It prompts the user to select an event and then retrieves the selected event from the list.
        If the selected event is not found, it displays an error message.

        Args:
            list_of_events (List[Event]): The list of events from which the user will select.

        Returns:
            Optional[Event]: The selected event if found, otherwise None.
        """
        self.view_cli.clear_screen()

        # Display the list of events for user selection
        self.view_cli.display_events_for_selection(list_of_events)

        # Retrieve the IDs of all events in the list.
        events_ids = [event.id for event in list_of_events]

        # Prompt the user to select a collaborators in the list.
        self.view_cli.display_info_message("Select the event to which you want modify/add the support contact")
        selected_event_id = self.view_cli.prompt_for_selection_by_id(events_ids, "Event")

        # Find the selected event from the list based on selected event id.
        selected_event = next((event for event in list_of_events if event.id == selected_event_id), None)

        if not selected_event:
            # If selected event is not found, display error message
            self.view_cli.display_error_message("We couldn't find the event. Please try again later.")

        # Return the selected event.
        return selected_event

    def get_support_collaborators(self) -> List[Collaborator]:
        """
        Retrieves all collaborators with support role from the CRM service.

        If a database error occurs during retrieval, it displays an error message,
        and returns an empty list.
        If any other unexpected exception occurs, it displays an error message,
        and returns an empty list.
        If it finds no collaborators, it displays an information message.
        Finally, it returns the list of support collaborators.

        Returns:
            List[Collaborator]: A list of all support collaborators retrieved from the CRM service.
        """
        try:
            support_collaborators = self.services_crm.get_support_collaborators()
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(str(e))
            return []

        if not support_collaborators:
            # Display an information message if no collaborators are found.
            self.view_cli.display_info_message("There not support collaborators to display.")

        return support_collaborators

    def add_support_contact_to_event(self, event: Event, support_contact: Collaborator) -> Event:
        """
        Adds a support contact to an event.

        This method attempts to add a support contact to the specified event.
        It handles database errors and other unexpected exceptions.

        Args:
            event (Event): The event to which the support contact will be added.
            support_contact (Collaborator): The support contact to be added.

        Returns:
            Event: The event object with the new support contact added, if successful.
        """
        try:
            # Attempt to add the support contact to the event.
            event_with_new_support_contact = self.services_crm.add_support_contact_to_event(event, support_contact)
            return event_with_new_support_contact
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(srt(e))

# ================================== 5 - View all clients.       =======================================================
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

# ================================== 6 - View all contracts.     =======================================================
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

# ================================== 7 - View all events.        =======================================================
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

# ================================== 8 - Exit the CRM system.    =======================================================
    def exit_of_crm_system(self) -> None:
        self.view_cli.clear_screen()
        self.view_cli.display_info_message("Thank you for using CRM Events, until next time!")

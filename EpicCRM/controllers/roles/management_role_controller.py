from typing import Optional
from typing import List
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.db.models.query import QuerySet
from crm.models import Collaborator
from crm.models import Client
from crm.models import Contract
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

    def __init__(self, collaborator: Collaborator,
                 services_crm: ServicesCRM,
                 view_cli: ManagementRoleViewCli):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli

    def start(self):
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
                # TODO: Filter and display events, for example, show all events without an assigned 'support' contact.
                pass
            case 4:
                # TODO: Assign or change the 'support' collaborator associated with an event.
                pass
            case 5:
                # TODO: View the list of all clients.
                pass
            case 6:
                # TODO:View the list of all contracts.
                pass
            case 7:
                # TODO: View the list of all events.
                pass
            case 8:
                #  Exit the CRM system.
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

    # ============================== 1 - Manage Collaborators.   =======================================================
    def manage_collaborators(self) -> None:
        self.view_cli.clear_screen()

        # Check if the collaborator has the "manage_collaborator" permission which allows CRUD operations on
        # collaborators.
        if not self.collaborator.has_perm("crm.manage_collaborators"):
            self.view_cli.display_error_message("You do not have permission to manage collaborators.")
            return

        # Shows the sub menu for manage collaborators
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
                # Return to main menu
                self.start()
            case _:
                self.view_cli.display_info_message("Invalid option selected. Please try again.")
                return

    def process_collaborator_creation(self) -> None:
        while True:
            self.view_cli.clear_screen()
            self.view_cli.display_info_message("Registering new collaborator...")
            data_collaborator = self.view_cli.get_data_for_create_collaborator()

            try:
                collaborator = self.services_crm.register_collaborator(**data_collaborator)
                self.view_cli.clear_screen()
                self.view_cli.display_collaborator_details(collaborator)
                self.view_cli.display_info_message("User registered successfully!")
                break
            except ValidationError as e:
                self.view_cli.display_error_message(str(e))
                continue_operation = self.view_cli.get_user_confirmation("Do you want try again?")
                if not continue_operation:
                    break
            except Exception as e:
                self.view_cli.display_error_message(str(e))
                break

    def process_collaborator_modification(self) -> None:
        self.view_cli.clear_screen()

        collaborators = self.get_all_collaborators()
        if not collaborators:
            return
        selected_collaborator = self.select_collaborator_from(collaborators)
        if not selected_collaborator:
            return
        self.modify_collaborator(selected_collaborator)

    def select_collaborator_from(self, list_of_collaborators: List[Collaborator]) -> Optional[Collaborator]:
        self.view_cli.clear_screen()
        self.view_cli.display_collaborators_for_selection(list_of_collaborators)
        collaborators_ids = [collaborator.id for collaborator in list_of_collaborators]
        selected_collaborator_id = self.view_cli.prompt_for_selection_by_id(collaborators_ids, "Collaborator")

        selected_collaborator = next((collaborator for collaborator in list_of_collaborators
                                      if collaborator.id == selected_collaborator_id), None)

        if not selected_collaborator:
            self.view_cli.display_error_message("We couldn't find the collaborator. Please try again later.")

        return selected_collaborator

    def get_all_collaborators(self) -> List[Collaborator]:
        try:
            collaborators = self.services_crm.get_all_non_superuser_collaborators()
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(f"{e}")
            return []

        if not collaborators:
            self.view_cli.display_info_message("There are no collaborators available to display.")

        return collaborators

    def modify_collaborator(self, selected_collaborator: Collaborator) -> None:
        while True:
            self.view_cli.display_collaborator_details(selected_collaborator)
            collaborator_data = self.view_cli.get_data_for_modify_collaborator(selected_collaborator.get_full_name())

            if not collaborator_data:
                self.view_cli.display_info_message("No modifications were made.")
                return

            try:
                collaborator_modified = self.services_crm.modify_collaborator(selected_collaborator, collaborator_data)
                self.view_cli.clear_screen()
                self.view_cli.display_collaborator_details(collaborator_modified)
                self.view_cli.display_info_message("The collaborator has been modified successfully.")
                break
            except ValidationError as e:
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
        self.view_cli.display_warning_message(f"You have selected: {self.collaborator.get_full_name()} for deletion.")
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

    # ============================== 2 - Manage Contracts.       =======================================================
    def manage_contract(self) -> None:
        self.view_cli.clear_screen()

        # Check if the collaborator has the "manage_contracts_creation_modification" permission
        # which allows modification and update operations on contracts.
        if not self.collaborator.has_perm("crm.manage_contracts_creation_modification"):
            self.view_cli.display_error_message("You do not have permission to manage contracts.")
            return

        # Shows the sub menu for manage contracts.
        self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_MANAGE_CONTRACTS)

        # captures their choice.
        choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_MANAGE_CONTRACTS))

        match choice:
            case 1:
                # Create  a contract in the CRM system
                self.process_contract_creation()
            case 2:
                #  Update a contract in the CRM system
                self.process_contract_modification()
            case 3:
                # Return to main menu
                self.start()
            case _:
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

        # Prompt user to select client by ID
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
        self.view_cli.clear_screen()

        contracts = self.get_all_contracts()
        if not contracts:
            return
        selected_contract = self.select_contract_from(contracts)
        if not selected_contract:
            return
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

    # ============================== 9 - Exit the CRM system.    =======================================================
    def exit_of_crm_system(self) -> None:
        self.view_cli.clear_screen()
        self.view_cli.display_info_message("Thank you for using CRM Events, until next time!")

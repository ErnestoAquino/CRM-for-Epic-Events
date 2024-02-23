from django.core.exceptions import PermissionDenied
from django.db import DatabaseError
from sentry_sdk import capture_message
from sentry_sdk import capture_exception
from typing import List
from typing import Optional

from crm.models import Collaborator
from crm.models import Event
from crm.models import Client
from crm.models import Contract

from services.services_crm import ServicesCRM

from controllers.models.client_controller import ClientController
from controllers.models.contract_controller import ContractController
from controllers.models.event_controller import EventController
from views.roles.support_role_view_cli import SupportRoleViewCli


class SupportRoleController:
    def __init__(self, collaborator: Collaborator,
                 services_crm: ServicesCRM,
                 view_cli: SupportRoleViewCli):

        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli

    def start(self) -> None:
        """
        Initiates the CRM system for the logged-in collaborator.

        This method displays a welcome message to the collaborator and presents the main menu.
        It captures the collaborator's choice and directs them to the corresponding functionality.
        After completing an action, it prompts the collaborator if they want to continue or exit the system.
        If the collaborator chooses to exit, the method exits the CRM system.

        Returns:
            None
        """
        self.view_cli.display_info_message(f"Hi! {self.collaborator.get_full_name()}")

        # Shows the main menu to the collaborator
        self.view_cli.show_main_menu(collaborator=self.collaborator)

        # captures their choice.
        choice = self.view_cli.get_user_menu_choice()

        match choice:
            case 1:
                # Presents the list of all clients.
                self.show_all_clients()
            case 2:
                # Presents the list of all contracts.
                self.show_all_contracts()
            case 3:
                # Presents the list of all events.
                self.show_all_events()
            case 4:
                # Presents events assigned to the collaborator.
                self.show_events_for_collaborator()
            case 5:
                # Initiates the modification process for an event.
                self.process_event_modification()
            case 6:
                # Exits the CRM system.
                self.exit_of_crm_system()
                return
            case _:
                capture_message(
                    f"Invalid menu option selected: {choice}. in start() at support controller"
                    f"Expected options were between 1 and 6.",
                    level = 'error')
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

# ================================== 1 - View all clients.       =======================================================
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
            self.view_cli.display_info_message("You do not have permission to view the list of clients.")
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
# ================================== 2 - View all contracts.     =======================================================

    def show_all_contracts(self) -> None:
        """
        Displays the list of all contracts.

        This method checks if the current collaborator has permission to view the list of contracts.
        If permission is granted, it retrieves the list of all contracts
        and displays them.
        If no contracts are found or if the collaborator does not have permission,
        it returns without displaying anything.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Check if the collaborator has permission to view contracts
        if not self.collaborator.has_perm("crm.view_contract"):
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to the list of contracts", level="info")
            self.view_cli.display_info_message("You do not have permission to view the list of contracts.")
            return

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

# ================================== 3 - View all events.        =======================================================
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
            return

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
            contact requirement should be filtered.
            Defaults to None.
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

# ====================== 4 - Presents events assigned to the collaborator.  ============================================
    def show_events_for_collaborator(self) -> None:
        """
        Displays events associated with the current collaborator.

        This method checks if the current collaborator has permission to view events.
        If the collaborator has permission, it retrieves events associated with the collaborator.
        If events are found, it displays the list of events for the collaborator.
        If no events are found, it returns without displaying anything.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        if not self.collaborator.has_perm("crm.view_event"):
            capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to the list of events for the collaborator.", level="info")
            self.view_cli.display_error_message("You do not have permission to view the list of events.")
            return

        # Retrieve events associated with the current collaborator.
        events_for_collaborator = self.get_events_for_collaborator(self.collaborator.id)

        if not events_for_collaborator:
            # If no events are found, return
            return

        # Display the list of events associated with the collaborator.
        self.view_cli.display_list_events_for_collaborator(events_for_collaborator, collaborator=self.collaborator)

    def get_events_for_collaborator(self, collaborator_id: int) -> List[Event]:
        """
        Retrieves a list of events associated with the current collaborator.

        This method attempts to fetch events associated with the current collaborator from the CRM service.
        If successful, it returns the list of events.
        If a database error occurs, it displays an error message
        and returns an empty list.
        If any other exception occurs, it displays the exception message and returns
        an empty list.
        If no events are found, it displays an info message and returns an empty list.

        Returns:
            List[Event]: A list of events associated with the current collaborator,
            or an empty list if no events are found or if an error occurs.
        """

        try:
            # Attempt to retrieve events associated with the current collaborator
            events = self.services_crm.get_events_for_collaborator(collaborator_id)
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(str(e))
            return []

        if not events:
            # Display an information message if no events are found.
            self.view_cli.display_info_message("There is no events available to display.")

        return events

# ============================== 5 - Modify Event  =====================================================================
    def process_event_modification(self) -> None:
        """
        Handles the modification of an event associated with the current collaborator.

        Retrieves events associated with the current collaborator.
        It then checks if there are events assigned to the collaborator.
        If there are no events, it returns without further action.
        If events are found, it proceeds to display them and asks the user to choose one for modification.
        If a selected event is not found, it returns without further action.

        Returns:
            None
        """
        self.view_cli.clear_screen()

        # Retrieve events associated with the current collaborator.
        events_for_collaborator = self.get_events_for_collaborator(self.collaborator.id)

        # Check if there are events assigned to the collaborator.
        if not events_for_collaborator:
            return

        # If there are events, proceed to display them and ask the user to choose one for modification.
        selected_event = self.select_event_from(events_for_collaborator)
        if not selected_event:
            return

        self.modify_event(selected_event)

    def select_event_from(self, events_for_collaborator: List[Event]) -> Optional[Event]:
        """
        Selects an event from the list of events.

        Displays the list of events for selection.
        Retrieve the IDs of all events in the list.
        Prompts the user to select an event by ID.
        Returns the selected collaborator from the list, if found.

        Args:
            events_for_collaborator (List[Collaborator]): The list of collaborators to choose from.
        Returns:
            Optional[Event]: The selected event, or None if not found.
        """
        self.view_cli.clear_screen()
        self.view_cli.display_events_for_selection(events_for_collaborator)

        # Display the list of events for user selection.
        self.view_cli.display_info_message("Please select the event you wish to modify.")
        events_ids = [event.id for event in events_for_collaborator]

        # Prompt the user to select a collaborator by ID.
        selected_event_id = self.view_cli.prompt_for_selection_by_id(events_ids, "Event")

        # Find the selected collaborator from the list based on the ID.
        selected_event = next((event for event in events_for_collaborator if event.id == selected_event_id), None)

        if not selected_event:
            self.view_cli.display_error_message("We couldn't find the event. Please try again later.")

        # Return the event collaborator.
        return selected_event

    def modify_event(self, event: Event) -> None:
        """
        Modifies the details of the provided event.

        Displays the details of the event to be modified, and prompts the user to enter modifications.
        It then attempts to modify the event using the provided data.
        If no modifications were provided, it informs the user and returns. If an error occurs during
        the modification process, it displays an appropriate error message.

        Args:
            event (Event): The event to be modified.

        Returns:
            None
        """
        # Clears the screen before proceeding.
        self.view_cli.clear_screen()

        # Displays the details of the event to be modified.
        self.view_cli.display_event_details(event)

        modifications = self.view_cli.prompt_for_event_modification()

        # Checks if no modifications were provided.
        if not modifications:
            self.view_cli.display_info_message("No modifications were made.")
            return

        try:
            # Attempts to modify event using the provided data.
            event_modified = self.services_crm.modify_event(event, modifications)
            self.view_cli.clear_screen()

            # Display the details of the event modified
            self.view_cli.display_event_details(event_modified)

            # Informs the user that the event has been modified successfully.
            self.view_cli.display_info_message("The event has been modified successfully.")
            return
        except ValidationError as e:
            self.view_cli.display_error_message(str(e))
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a error with the database access. "
                                                "Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))

# ============================== 6 - Exit of crm system  ===============================================================
    def exit_of_crm_system(self):
        self.view_cli.clear_screen()
        self.view_cli.display_info_message("Thank you for using CRM Events, until next time!")

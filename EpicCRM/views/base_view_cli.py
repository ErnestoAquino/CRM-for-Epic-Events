import re
from typing import List
from typing import Optional
from django.db.models.query import QuerySet
import click
from rich.box import ROUNDED
from rich.console import Console
from rich.table import Table
from rich.text import Text

from crm.models import Contract
from crm.models import Client
from crm.models import Event


class BaseViewCli:

    def ask_user_if_continue(self) -> bool:
        """
        Ask the user if they want to continue performing another operation.

        This method prompts the user with a question asking if they want to perform another operation.
        It expects a yes/no response and continues to prompt until a valid response is entered.

        Returns:
            bool: True if the user wants to continue, False if they do not.

        """
        while True:
            response = click.prompt("Do you want to perform another operation? (yes/no)", type=str).lower()
            if response == "yes":
                return True
            elif response == "no":
                return False
            else:
                self.display_error_message("Invalid response. Please enter 'yes' or 'no'.")

    def get_user_confirmation(self, question: str) -> bool:
        """
        Prompt the user for a yes/no confirmation.

        This method prompts the user with a given question and expects a yes/no answer.
        It continues to prompt until a valid response is entered.

        Args:
            question (str): The question to display to the user.

        Returns:
            bool: True if the user confirms with 'yes', False if the user responds with 'no'.

        """
        while True:
            response = click.prompt(f"{question} (yes/no)", type=str).lower()
            if response == "yes":
                return True
            elif response == "no":
                return False
            else:
                self.display_error_message("Invalid response. Please enter 'yes' or 'no'.")

    def get_collaborator_choice(self, limit: int) -> int:
        """
        Prompt the user to choose an option within a specified limit.

        This method prompts the user to choose an option within the specified limit.
        It continues to prompt until a valid option is entered.

        Args:
            limit (int): The upper limit of the options available.

        Returns:
            int: The chosen option.
        """
        while True:
            choice = click.prompt("Please choose an option", type=int)
            if 1 <= choice <= limit:
                return choice
            else:
                self.display_error_message("Invalid option. Please try again.")

    def prompt_for_selection_by_id(self, ids: [int], model_name: str) -> int:
        """
        Prompt the user to select an ID from a list.

        This method prompts the user to enter the ID of the selected model from a list of IDs.
        It continues to prompt until a valid ID is entered.

        Args:
            ids (List[int]): A list of integers representing the available IDs.
            model_name (str): The name of the model for which the ID is being selected.

        Returns:
            int: The selected ID.
        """
        # Ask the user to choose an ID
        while True:
            selected_id = click.prompt(f"Please enter the ID of the {model_name} you wish to select.", type=int)
            if selected_id in ids:
                return selected_id
            else:
                self.display_error_message(f"Invalid {model_name} ID. Please choose of the list.")

    @staticmethod
    def clear_screen() -> None:
        """
        Clear the console screen using the `click.clear()` function.
        """
        click.clear()

    @staticmethod
    def display_error_message(error_message: str) -> None:
        """
        Display an error message in the console with a bold red style.
        Args:
            error_message (str): The error message to be displayed.
        """

        console = Console()
        error_text = Text(error_message, style="bold red")
        console.print(error_text)

    @staticmethod
    def display_info_message(info_message: str) -> None:
        """
        Display an information message in the console with a bold green style.
        Args:
            info_message (str): The information message to be displayed.
        """
        console = Console()
        info_text = Text(info_message, style="bold green")
        console.print(info_text)

    @staticmethod
    def display_message(message: str) -> None:
        """
        Display a message in the console bold magenta style.
        Args:
            message (str): The message to be displayed.
        """
        console = Console()
        message_text = Text(message, style="bold magenta")
        console.print(message_text)

    @staticmethod
    def display_warning_message(message: str) -> None:
        """
        Display a warning message in the console with a bold yellow style.
        Args:
            message (str): The warning message to be displayed.
        """
        console = Console()
        message_text = Text(message, style="bold yellow")
        console.print(message_text)

    @staticmethod
    def display_list_of_events(events: List[Event]) -> None:
        """
        Display a list of events in a table format.

        This method takes a list of Event objects and displays them in a table format using the Rich library.

        Args:
            events (List[Event]): A list of Event objects to be displayed.

        Returns:
            None
        """

        # Create console instance.
        console = Console()

        # Create table
        table = Table(title="List of Events",
                      show_header=True,
                      header_style="bold magenta",
                      expand=True,
                      show_lines=True)

        table.add_column("ID", style="dim", width=10)
        table.add_column("Contract ID", style="dim", width=12)
        table.add_column("Name", style="dim", width=12)
        table.add_column("Client Name", style="dim", width=20)
        table.add_column("Support Contact", style="dim", width=20)
        table.add_column("Start Date", style="dim", width=20)
        table.add_column("End Date", style="dim", width=20)
        table.add_column("Location", style="dim", width=25)
        table.add_column("Attendees", justify="right", style="dim", width=12)
        table.add_column("Notes", style="dim", width=30)

        # Fill the table with events' data
        for event in events:
            event_name = event.name if event.name else "No Named"
            contract_id = str(event.contract.id) if event.contract else "No Contract"
            client_name = event.client_name
            support_contact_name = event.support_contact.get_full_name() if event.support_contact else ("No Contact "
                                                                                                        "Assigned")
            start_date = event.start_date.strftime("%Y-%m-%d %H:%M")
            end_date = event.end_date.strftime("%Y-%m-%d %H:%M")
            location = event.location
            attendees = str(event.attendees)
            notes = event.notes if event.notes else "No Notes"

            table.add_row(
                str(event.id),
                contract_id,
                event_name,
                client_name,
                support_contact_name,
                start_date,
                end_date,
                location,
                attendees,
                notes
            )

        # Print the table using Rich
        console.print(table)

    @staticmethod
    def display_list_of_clients(clients: List[Client]) -> None:
        """
        Display a list of clients in a table format.
        This method takes a list of clients and displays them in a table format using the Rich library.

        Args:
            clients (List[Client]): A list of clients to be displayed.

        Returns:
            None
        """

        # Create console instance.
        console = Console()

        # Create table
        table = Table(title="List of all Clients",
                      show_header=True,
                      header_style="bold magenta",
                      expand=True,
                      box=ROUNDED)

        table.add_column("Full Name", style="dim", width=20)
        table.add_column("Email", style="dim", width=20)
        table.add_column("Phone", justify="right", style="dim", width=12)
        table.add_column("Company Name", style="dim", width=20)
        table.add_column("Creation Date", style="dim", width=20)

        # Fill the table with clients' data
        for client in clients:
            table.add_row(
                client.full_name,
                client.email,
                client.phone,
                client.company_name,
                client.creation_date.strftime("%Y-%m-%d %H:%M")
            )

        # Print the table using Rich
        console.print(table)

    @staticmethod
    def display_list_of_contracts(contracts: List[Contract]) -> None:
        """
        Display a list of contracts in a table format.

        This method takes a list of contracts and displays them in a tabular format,
        including details such as contract ID, client name, sales contact, total amount,
        amount remaining, creation date, and status.

        Args:
            contracts (List[Contract]): A list of contracts to be displayed.

        Returns:
            None
        """

        # Create console instance.
        console = Console()

        # Create table
        table = Table(title="List of all Contracts", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Client Name", style="dim", width=20)
        table.add_column("Sales Contact", style="dim", width=20)
        table.add_column("Total Amount", justify="right", style="dim", width=12)
        table.add_column("Amount Remaining", justify="right", style="dim", width=15)
        table.add_column("Creation Date", style="dim", width=20)
        table.add_column("Status", style="dim", width=15)

        # Fill the table with contracts' data
        for contract in contracts:
            client_name = contract.client.full_name if contract.client else "No Client Assigned"
            sales_contact_name = contract.sales_contact.get_full_name() if contract.sales_contact else ("No Contact "
                                                                                                        "Assigned")
            total_amount = f"${contract.total_amount:.2f}"
            amount_remaining = f"${contract.amount_remaining:.2f}"
            creation_date = contract.creation_date.strftime("%Y-%m-%d %H:%M")

            # get_status_display() to get the human-readable version of a ChoiceField
            status = contract.get_status_display()

            table.add_row(
                str(contract.id),
                client_name,
                sales_contact_name,
                total_amount,
                amount_remaining,
                creation_date,
                status
            )

        # Print the table using Rich
        console.print(table)

    # ==========================  Management Controller    ===============================

    def show_menu(self, collaborator_name: str, menu_options: List[str]) -> None:
        """
        Display a menu with options for the user.

        This method displays a menu of options for the user to choose from.
        It includes a greeting message with the collaborator's name and prompts the user to select
        an operation from the provided list of menu options.

        Args:
            collaborator_name (str): The name of the collaborator.
            menu_options (List[str]): A list of menu options to be displayed.

        Returns:
            None
        """
        self.clear_screen()
        console = Console()

        # Create a table for the menu options.
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Menu Options", justify="left", style="dim")

        # Add menu options to the table
        for option in menu_options:
            table.add_row(option)

        self.display_info_message(f"Welcome {collaborator_name}.")
        self.display_info_message("What operation would you like to perform?\n")

        # Print table (menu options)
        console.print(table)

    def get_valid_input_with_limit(self, prompt_text: str, max_length: int, allow_blank: bool = False) -> str:
        """
        Prompt the user for input within a specified limit.

        This method prompts the user for input using Click library. It ensures that the input
        is not empty and does not exceed the specified maximum length. If allow_blank is True,
        it allows blank input. Otherwise, it displays a warning message for empty input.

        Args:
            prompt_text (str): The text to prompt the user for input.
            max_length (int): The maximum length allowed for the input.
            allow_blank (bool, optional): Whether blank input is allowed. Defaults to False.

        Returns:
            str: The valid input from the user.
        """

        # Loop to ensure valid input within the specified limit or allow blank input.
        while True:
            # Prompts the user for input.
            user_input = click.prompt(prompt_text, type=str, default="", show_default=False).strip()

            # Checks if the input is empty and blank inputs are allowed.
            if allow_blank and user_input == "":
                return user_input

            # Checks if the input is empty and blank inputs are not allowed.
            if not user_input:
                self.display_warning_message(f"{prompt_text} cannot be empty.")
                continue

            # Checks if the input exceeds the maximum length.
            if len(user_input) > max_length:
                self.display_warning_message(f"{prompt_text} must not exceed {max_length} characters.")
                continue

            # Returns the valid input if it's not empty or exceeds the length limit
            return user_input

    def get_valid_email(self, allow_blank: bool = False) -> str:
        """
        Prompts the user for a valid email address.

        This method prompts the user to enter an email address and validates the input.
        If 'allow_blank' is set to True, it allows the input to be empty (blank).
        It displays warning messages if the input is empty or error messages if the email format is invalid.

        Args:
            allow_blank (bool, optional): Whether to allow blank input (default is False).

        Returns:
            str: The validated email address entered by the user.
        """
        email_regex = r'\b[A-Z|a-z|0-9|._%+-]+@[A-Z|a-z|0-9|.-]+\.[A-Z|a-z]{2,}\b'
        while True:
            email = click.prompt("Email", type=str, default="", show_default=False).strip()

            # Check if input is blank and allow_blank is True
            if allow_blank and email == "":
                return email

            # Check if input is empty
            if not email:
                self.display_warning_message("Email cannot be empty.")
                continue

            # Check if input matches email regex pattern
            if not re.fullmatch(email_regex, email):
                self.display_error_message(
                    "Invalid email format. Please enter a valid email address, such as example@domain.com.")
                continue
            return email

    def get_valid_decimal_input(self, prompt_text: str, allow_blank: bool = False) -> Optional[float]:
        """
        Prompts the user for a valid decimal input.

        This method prompts the user with a specified prompt text to enter a decimal number.
        It validates the input and returns the decimal value entered by the user.
        If 'allow_blank' is set to True, it allows the input to be empty (None).

        Args:
            prompt_text (str): The prompt text to display to the user.
            allow_blank (bool, optional): Whether to allow blank input (default is False).

        Returns:
            Optional[float]: The validated decimal value entered by the user, or None if input is blank.
        """
        while True:
            user_input = click.prompt(prompt_text, default="", show_default=False).strip()

            # Check if input is blank and allow_blank is True
            if allow_blank and user_input == "":
                return None

            # Check if input is empty and allow_blank is False
            if not user_input and not allow_blank:
                self.display_error_message("This field cannot be empty.")
                continue

            try:
                # Convert input to float and check if it's positive
                value = float(user_input)
                if value < 0:
                    self.display_error_message("Please enter a positive decimal number (e.g. 9999.99)")
                    continue
                return value
            except ValueError:
                # Handle non-numeric input
                self.display_error_message("Please enter a positive decimal number (e.g. 9999.99)")
                continue

    def get_valid_choice(self, prompt_text: str,
                         choices: List[str],
                         allow_blank: bool = False) -> Optional[str]:
        """
        Prompts the user for a valid status for a contract.

        This method prompts the user with a specified prompt text to choose a status for a contract.
        It validates the input against a list of valid choices and returns the chosen status.
        If 'allow_blank' is set to True, it allows the input to be empty (None).
        It displays error messages if the input is invalid or empty.

        Args:
            prompt_text (str): The prompt text to display to the user.
            choices (List[str]): A list of valid choices for the status.
            allow_blank (bool, optional): Whether to allow blank input (default is False).

        Returns:
            Optional[str]: The validated status chosen by the user, or None if input is blank.
        """
        while True:
            choice = click.prompt(prompt_text, default="", show_default=False).strip().lower()

            # Check if input is blank and allow_blank is True
            if allow_blank and choice == "":
                return None

            # Check if input is empty
            if not allow_blank and choice == "":
                self.display_error_message("Status cannot be empty.")
                continue

            # Check if input is in the list of valid choices
            if choice not in choices:
                self.display_error_message(f"Invalid choice. Please choose from ({', '.join(choices)}).")
                continue

            return choice

    # ==========================  Sales Controller    ===============================

    def display_contract_details(self, contract: Contract) -> None:
        """
        Display details of a contract.

        This method create a table to display detailed information about a contract.
        It includes contract ID, client information, sales contact, total amount, amount remaining, creation date,
        and status. The table is then printed using the Rich library for terminal output.

        Args:
            contract (Contract): The Contract object whose details are to be displayed.
        """

        console = Console()
        self.clear_screen()

        # Create a table to display contract details
        table = Table(title="Contract Detail",
                      show_header=True,
                      header_style="bold blue",
                      show_lines=True)

        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width=40)

        # Add rows to the table with contract details
        table.add_row("Contract ID", str(contract.id))
        table.add_row("Client Information", contract.client.full_name + " - " + contract.client.email)
        table.add_row("Sales Contact", contract.sales_contact.get_full_name() if contract.sales_contact else "N/A")
        table.add_row("Total Amount", str(contract.total_amount))
        table.add_row("Amount Remaining", str(contract.amount_remaining))
        table.add_row("Creation Date", contract.creation_date.strftime("%Y-%m-%d"))
        table.add_row("Status", "Signed" if contract.status == "signed" else "Not Signed")

        console.print(table, justify="center")

    def display_clients_for_selection(self, clients: List[Client]) -> None:
        """
        Display a list of clients for selection.

        This method creates a table to display a list of available clients
        for selection. It includes client ID and full name in the table. The table is then printed
        using the Rich library for terminal output.

        Args:
            clients (List[Client]): A list of Client objects to display for selection.
        """

        self.clear_screen()
        # Create console instance
        console = Console()

        # Create table
        table = Table(title="List of Available Clients", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Full Name", style="dim", width=20)

        # Fill the table with clients data
        for client in clients:
            client_name = client.full_name if client.full_name else "No Name"

            table.add_row(
                str(client.id),
                client_name
            )

        # Print the table using Rich
        console.print(table)

    def display_client_details(self, client: Client) -> None:
        """
        Display details of a client.

        This method clears the screen and creates a table to display the details of the given client,
        including client ID, full name, email, phone number, company name, and sales contact. The table
        is then printed using the Rich library for terminal output.

        Args:
            client (Client): The client object whose details are to be displayed.
        """
        self.clear_screen()
        console = Console()

        # Create a table to display client details
        table = Table(title="Client Detail", show_header=True, header_style="bold blue", show_lines=True)
        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width=40)

        # Add rows to the table with client details
        table.add_row("Client ID", str(client.id))
        table.add_row("Full Name", client.full_name)
        table.add_row("Email", client.email)
        table.add_row("Phone", client.phone)
        table.add_row("Company Name", client.company_name)
        table.add_row("Sales Contact", client.sales_contact.get_full_name() if client.sales_contact else "N/A")

        # Print the table
        console.print(table, justify="center")

    def display_contracts_for_selection(self, contracts: List[Contract]) -> None:
        """
        Display a list of available contracts for selection.

        This method clears the screen, creates a table to display the available contracts along with
        their ID, client name, and status. The table is printed using the Rich library for terminal
        output.

        Args:
            contracts (List[Contract]): A list of contracts to display.
        """
        self.clear_screen()
        # Create console instance
        console = Console()

        # Create table
        table = Table(title="List of Available Contracts", show_header=True, header_style="bold magenta",
                      expand=True)
        table.add_column("Contract ID", style="dim", width=12)
        table.add_column("Client Name", width=20)
        table.add_column("Status", width=12)

        # Fill the table with contracts data
        for contract in contracts:
            client_name = contract.client.full_name if contract.client.full_name else "No Name"
            status = contract.get_status_display()

            table.add_row(
                str(contract.id),
                client_name,
                status
            )

        # Print the table using Rich
        console.print(table)

    # ==========================  Support Controller    ===============================

    @staticmethod
    def display_events_for_selection(events: List[Event]) -> None:
        """
        Display a list of available events for selection.

        This static method creates a table to display the available events along with their ID, name,
        client name, and support contact. The table is printed using Rich library for terminal
        output.

        Args:
            events (List[Event]): A list of events to display.
        """

        # Create console instance
        console = Console()

        # Create table
        table = Table(title="List of Available Events", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Name", style="dim", width=20)
        table.add_column("Client Name", style="dim", width=20)
        table.add_column("Support Contact", style="dim", width=20)

        # Fill the table with events data
        for event in events:
            event_name = event.name if event.name else "No Name"
            client_name = event.client_name
            support_contact = event.support_contact.get_full_name() if event.support_contact else "N/A"

            table.add_row(
                str(event.id),
                event_name,
                client_name,
                support_contact
            )

        # Print the table using Rich
        console.print(table)

    @staticmethod
    def display_event_details(event: Event) -> None:
        """
        Display the details of an event in a formatted table.

        This method creates a table to display various details of the provided event,
        including its ID, name, client details, start and end dates, location, attendees,
        support contact, and any additional notes.

        Args:
            event (Event): The event object containing details to display.
        """
        console = Console()

        # Create a table to display event details
        table = Table(title="Event Detail", show_header=True, header_style="bold blue", show_lines=True)
        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width=40)

        # Add rows to the table with event details
        table.add_row("Event ID", str(event.id))
        table.add_row("Name", event.name)
        table.add_row("Client Name", event.client_name)
        table.add_row("Client Contact", event.client_contact or "N/A")
        table.add_row("Start Date", event.start_date.strftime("%Y-%m-%d %H:%M"))
        table.add_row("End Date", event.end_date.strftime("%Y-%m-%d %H:%M"))
        table.add_row("Location", event.location)
        table.add_row("Attendees", str(event.attendees))
        table.add_row("Support Contact", event.support_contact.get_full_name() if event.support_contact else "N/A")
        table.add_row("Notes", event.notes or "N/A")

        # Print the table
        console.print(table, justify="center")

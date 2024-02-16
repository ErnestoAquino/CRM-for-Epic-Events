import re
import click
from django.db.models.query import QuerySet
from rich.console import Console
from rich.table import Table
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.timezone import get_default_timezone
from dateutil.parser import parse

from views.base_view_cli import BaseViewCli

from crm.models import Client
from crm.models import Contract
from crm.models import Event


class SalesRoleViewCli(BaseViewCli):
    MENU_OPTIONS = [
        "1 - Create a new client.",
        "2 - Update client information.",
        "3 - Modify/update client contracts.",
        "4 - Filter and display contracts (e.g., unsigned or not fully paid).",
        "5 - Create an event for a client who has signed a contract.",
        "6 - View the list of all clients.",
        "7 - View the list of all contracts.",
        "8 - View the list of all events.",
        "9 - Exit the CRM system."
    ]
    MENU_LIMIT = len(MENU_OPTIONS)
    VALID_STATUS_CHOICES = ["signed", "not_signed"]

    # EMAIL_REGEX Explanation:
    # This regular expression is used to validate email addresses based on specific criteria:
    # \b - Word boundary to ensure the pattern is matched at the beginning or end of a word.
    # [A-Z|a-z|0-9|._%+-]+ - The local part of the email address. It can include:
    #   * Uppercase and lowercase letters (A-Z, a-z)
    #   * Digits (0-9)
    #   * Special characters: dots (.), underscores (_), percent signs (%), plus signs (+), and hyphens (-)
    #   This part must appear at least once (+).
    # @ - The @ symbol, which is mandatory in email addresses to separate the local part from the domain part.
    # [A-Z|a-z|0-9|.-]+ - The domain part of the email address. It can include:
    #   * Uppercase and lowercase letters (A-Z, a-z)
    #   * Digits (0-9)
    #   * Special characters: dots (.) and hyphens (-)
    #   This part must appear at least once (+).
    # \. - A literal dot (.) to separate the domain from the top-level domain (TLD).
    # [A-Z|a-z|0-9]{2,10} - The top-level domain (TLD). It can include:
    #   * Uppercase and lowercase letters (A-Z, a-z)
    #   * Digits (0-9)
    #   This part must be between 2 and 10 characters long ({2,10}).
    # \b - Another word boundary to ensure the pattern is matched at the beginning or end of a word.
    # This regex ensures that the email addresses match common patterns and standards, but it may not cover all
    # valid email formats as defined by the RFC standard.

    EMAIL_REGEX = r'\b[A-Z|a-z|0-9|._%+-]+@[A-Z|a-z|0-9|.-]+\.[A-Z|a-z|0-9]{2,10}\b'

    def show_main_menu(self, collaborator_name: str):
        self.clear_screen()
        console = Console()

        # Create a table for the menu options.
        table = Table(show_header=True,
                      header_style="bold magenta")

        table.add_column("Menu Options",
                         justify="left",
                         style="dim")

        # Add menu options to the table
        for option in self.MENU_OPTIONS:
            table.add_row(option)

        self.display_info_message(f"Welcome {collaborator_name}.")
        self.display_info_message(f"What operation wold you like to perform?\n")

        # Print table (menu options)
        console.print(table)

    def get_user_menu_choice(self) -> int:
        # Capture user choice
        choice = self.get_collaborator_choice(limit=self.MENU_LIMIT)

        return choice

    def get_data_for_add_new_client(self) -> dict:
        # Displays a message requesting information for the new client.
        self.display_info_message("Please provide the following information for the new client")

        # Loop to ensure valid input for the full name.
        while True:
            full_name = click.prompt("Full Name (max 100 characters)", type=str).strip()
            if not full_name:
                self.display_warning_message("Name cannot be empty.")
                continue
            if len(full_name) > 100:
                self.display_warning_message("Full Name must not exceed 100 characters.")
                continue
            break

        # Loop to ensure valid input for the email.
        while True:
            email = click.prompt("Email", type=str).strip()
            if not email:
                self.display_warning_message("Email cannot be empty.")
                continue
            if not re.fullmatch(self.EMAIL_REGEX, email):
                self.display_error_message("Invalid email format. Please enter a valid email address,"
                                           " such as example@domain.com.")
                continue
            break

        # Loop to ensure valid input for the phone number.
        while True:
            phone = click.prompt("Phone number (max 20 characters)", type=str).strip()
            if not phone:
                self.display_warning_message("Phone number cannot be empty.")
                continue
            if len(phone) > 20:
                self.display_warning_message("Phone number must not exceed 20 characters.")
                continue
            break

        # Loop to ensure valid input for the company name.
        while True:
            company_name = click.prompt("Company name (max 100 characters)", type=str).strip()
            if not company_name:
                self.display_warning_message("Company name cannot be empty.")
                continue
            if len(company_name) > 100:
                self.display_warning_message("Company name must not exceed 100 characters.")
                continue
            break

        # Constructs a dictionary containing the collected client data.
        client_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "company_name": company_name
        }

        return client_data

    def display_clients_for_selection(self, clients_queryset: QuerySet) -> None:
        self.clear_screen()
        # Create console instance
        console = Console()

        # Create table
        table = Table(title="List of Available Clients", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Full Name", style="dim", width=20)

        # Fill the table with clients data
        for client in clients_queryset:
            client_name = client.full_name if client.full_name else "No Name"

            table.add_row(
                str(client.id),
                client_name
            )

        # Print the table using Rich
        console.print(table)

    def display_client_details(self, client: Client) -> None:
        self.clear_screen()
        console = Console()

        # Create a table to display client details
        table = Table(title="Client Detail", show_header=True, header_style="bold blue", show_lines=True)
        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width = 40)

        # Add rows to the table with client details
        table.add_row("Client ID", str(client.id))
        table.add_row("Full Name", client.full_name)
        table.add_row("Email", client.email)
        table.add_row("Phone", client.phone)
        table.add_row("Company Name", client.company_name)
        table.add_row("Sales Contact", client.sales_contact.get_full_name() if client.sales_contact else "N/A")

        # Print the table
        console.print(table, justify="center")

    def prompt_for_client_modification(self) -> dict:
        modifications = {}
        self.display_info_message("Leave blank any field you do not wish to modify.")

        # Full Name Modification
        while True:
            new_full_name = click.prompt("New Full Name (max 100 characters)",
                                         default = "",
                                         show_default = False).strip()
            if not new_full_name:
                break
            if len(new_full_name) > 100:
                self.display_error_message("Full Name must not exceed 100 characters. Please try again.")
                continue
            modifications["full_name"] = new_full_name
            break

        # Email Modification
        while True:
            new_email = click.prompt("New Email", default = "", show_default = False).strip()
            if not new_email:
                break
            if not re.fullmatch(self.EMAIL_REGEX, new_email):
                self.display_error_message(
                    "Invalid email format. Please enter a valid email address, such as example@domain.com.")
                continue
            modifications["email"] = new_email
            break

        # Phone Number Modification
        while True:
            new_phone = click.prompt("New Phone number (max 20 characters)", default = "", show_default = False).strip()
            if not new_phone:
                break
            if len(new_phone) > 20:
                self.display_error_message("Phone number must not exceed 20 characters. Please try again.")
                continue
            modifications["phone"] = new_phone
            break

        # Company Name Modification
        while True:
            new_company_name = click.prompt("New Company name (max 100 characters)", default = "",
                                            show_default = False).strip()
            if not new_company_name:
                break
            if len(new_company_name) > 100:
                self.display_error_message("Company name must not exceed 100 characters. Please try again.")
                continue
            modifications["company_name"] = new_company_name
            break

        return modifications

    def display_contracts_for_selection(self, contracts_queryset: QuerySet) -> None:
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
        for contract in contracts_queryset:
            client_name = contract.client.full_name if contract.client.full_name else "No Name"
            status = contract.get_status_display()

            table.add_row(
                str(contract.id),
                client_name,
                status
            )

        # Print the table using Rich
        console.print(table)

    def display_contract_details(self, contract: Contract) -> None:
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

    def prompt_for_contract_modification(self) -> dict:
        modifications = {}
        self.display_info_message("Leave blank any field you do not wish to modify.")

        # Total amount modification
        while True:
            new_total_amount_str = click.prompt("New Total Amount (e.g., 9999.99)", default = "",
                                                show_default = False).strip()
            if not new_total_amount_str:
                break
            try:
                new_total_amount = float(new_total_amount_str)
                if new_total_amount <= 0:
                    self.display_error_message("Invalid total amount. Please enter a positive number.")
                    continue
                modifications["total_amount"] = "{:.2f}".format(new_total_amount)
                break
            except ValueError:
                self.display_error_message("Please enter a valid number.")
                continue

        # Amount Remaining Modification
        while True:
            new_amount_remaining_str = click.prompt("New Amount Remaining (e.g., 9999.99)", default = "",
                                                    show_default = False).strip()
            if not new_amount_remaining_str:
                break
            try:
                new_amount_remaining = float(new_amount_remaining_str)
                if new_amount_remaining < 0:
                    self.display_error_message("Invalid amount remaining. Please enter a non-negative number.")
                    continue
                modifications["amount_remaining"] = "{:.2f}".format(new_amount_remaining)
                break
            except ValueError:
                self.display_error_message("Please enter a valid number.")
                continue

        # Status Modification
        while True:
            new_status = click.prompt("New Status (Options: signed, not_signed)", default="",
                                      show_default=False).strip().lower()
            if not new_status:
                break
            if new_status not in self.VALID_STATUS_CHOICES:
                self.display_error_message("Invalid status. Please choose a valid status: signed or not_signed.")
                continue
            modifications["status"] = new_status
            break

        return modifications

    def get_contract_filter_choices(self) -> int:
        """
        Shows contract filter options and returns the user's choice as an integer.
        """
        self.clear_screen()
        console = Console()

        # Contract filtering options
        filter_options = [
            "1 - View all contracts of your clients.",
            "2 - View all unpaid contracts of your clients.",
            "3 - View all unsigned contracts of your clients."
        ]

        # Create a table for the menu options.
        table = Table(show_header=True,
                      header_style="bold magenta")

        table.add_column("Filter Options",
                         justify="left",
                         style="dim")

        # Add menu options to the table
        for option in filter_options:
            table.add_row(option)

        # Display filtering options to the user
        console.print(table, justify="center")

        choice = self.get_collaborator_choice(limit=len(filter_options))

        return choice

    def get_data_for_add_new_event(self) -> dict:
        self.display_info_message("Please provide the following information for the new event")

        client_name = self.get_valid_input_with_limit("Client Name", 100)
        name = self.get_valid_input_with_limit("Name", 255)
        client_contact = self.get_valid_input_with_limit("Client Contact", 1000)
        start_date = self.get_valid_start_date()
        end_date = self.get_valid_end_date(start_date)
        location = self.get_valid_input_with_limit("Location", 300)
        attendees = self.get_valid_input_positive_integer("Attendees")
        notes = click.prompt("Notes (optional)", default="", show_default=False).strip()

        event_data = {
            "client_name": client_name,
            "name": name,
            "client_contact": client_contact,
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "attendees": attendees,
            "notes": notes
        }
        return event_data

    def get_valid_input_with_limit(self, prompt_text: str, max_length: int) -> str:
        # Loop to ensure valid input within the specified limit.
        while True:
            # Prompts the user for input.
            user_input = click.prompt(prompt_text, type=str).strip()

            # Checks if the input is empty.
            if not user_input:
                self.display_warning_message(f"{prompt_text} cannot be empty.")
                continue

            # Checks if the input exceeds the maximum length.
            if len(user_input) > max_length:
                self.display_warning_message(f"{prompt_text} must not exceed {max_length} characters.")
                continue

            # Returns the valid input.
            return user_input

    def get_valid_input_positive_integer(self, prompt_text: str) -> int:
        while True:
            user_input_str = click.prompt(prompt_text, default = "", show_default = False)
            try:
                # Attempts to convert the input to an integer.
                user_input_int = int(user_input_str)
            except ValueError:
                # If the input cannot be converted to an integer, display an error message.
                self.display_error_message("Please enter a valid integer.")
                continue

            # Checks if the input is a positive integer.
            if user_input_int <= 0:

                # If the input is not positive, display an error message.
                self.display_error_message("The number must be greater than zero. Please try again.")
                continue

            # Returns the valid positive integer.
            return user_input_int

    def get_valid_start_date(self) -> datetime:
        # Loop to ensure valid input for the start date.
        while True:
            start_date_str = click.prompt("New start date (YYYY-MM-DD HH:MM)", default = "", show_default = False)
            try:

                # Attempts to parse the input string into a datetime object.
                naive_start_date = parse(start_date_str)
            except ValueError:

                # If the input cannot be parsed, display an error message.
                self.display_error_message("Invalid date format. Please use YYYY-MM-DD HH:MM.")
                continue

            # Checks if the start date is in the future.
            if naive_start_date < datetime.now():
                self.display_error_message("Start date must be in the future. Please try again.")
                continue

            # Converts the naive start date to an aware datetime object and returns it.
            return make_aware(naive_start_date, get_default_timezone())

    def get_valid_end_date(self, start_date: datetime) -> datetime:
        # Loop to ensure valid input for the end date.
        while True:
            end_date_str = click.prompt("New end date (YYYY-MM-DD HH:MM)", default = "", show_default = False)
            try:

                # Attempts to parse the input string into a datetime object.
                naive_end_date = parse(end_date_str)
                aware_end_date = make_aware(naive_end_date, get_default_timezone())
            except ValueError:

                # If the input cannot be parsed, display an error message.
                self.display_error_message("Invalid date format. Please use YYYY-MM-DD HH:MM.")
                continue
                # Checks if the end date is before or equal to the start date.
            if aware_end_date <= start_date:

                # If the end date is not after the start date, display an error message.
                self.display_error_message("End date must be after start date. Please try again.")
                continue

                # Returns the valid end date.
            return aware_end_date

    def display_event_details(self, event: Event) -> None:

        console = Console()
        self.clear_screen()

        table = Table(title = "Event Detail",
                      show_header = True,
                      header_style = "bold blue",
                      show_lines = True)

        table.add_column("Field", style = "dim", width = 20)
        table.add_column("Value", width = 40)

        table.add_row("Event ID", str(event.id))
        table.add_row("Contract ID", str(event.contract.id))
        table.add_row("Client Name", event.client_name)
        table.add_row("Event Name", event.name)
        table.add_row("Client Contact", event.client_contact)
        table.add_row("Start Date", event.start_date.strftime("%Y-%m-%d %H:%M"))
        table.add_row("End Date", event.end_date.strftime("%Y-%m-%d %H:%M"))
        support_contact_name = event.support_contact.get_full_name() if event.support_contact else "N/A"
        table.add_row("Support Contact", support_contact_name)
        table.add_row("Location", event.location)
        table.add_row("Attendees", str(event.attendees))
        table.add_row("Notes", event.notes or "N/A")

        console.print(table, justify = "center")

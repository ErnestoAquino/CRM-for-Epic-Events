import re
import click
from django.db.models.query import QuerySet
from rich.console import Console
from rich.table import Table

from views.base_view_cli import BaseViewCli

from crm.models import Client


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

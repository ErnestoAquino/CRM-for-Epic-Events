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
        """
        Display the main menu to the user.

        This method prints the main menu options in a table format,
        along with a welcome message addressed to the collaborator.

        Args:
            collaborator_name (str): The name of the collaborator to whom the welcome message is addressed.
        """
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
        """
        Prompt the user to provide information for creating a new client.

        This method displays a series of prompts to collect information required to create a new client.
        It ensures that the input provided by the user is valid and within specified limits.

        Returns:
            dict: A dictionary containing the collected client data.
        """

        # Displays a message requesting information for the new client.
        self.display_info_message("Please provide the following information for the new client")

        full_name = self.get_valid_input_with_limit("Full Name (max 100 characters)", 100)
        email = self.get_valid_email()
        phone = self.get_valid_input_with_limit("Phone number (max 20 characters)", 20)
        company_name = self.get_valid_input_with_limit("Company name (max 100 characters)", 100)

        # Constructs a dictionary containing the collected client data.
        client_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "company_name": company_name
        }

        return client_data

    def get_data_for_client_modification(self) -> dict:
        """
        Prompt the user to provide information for modifying a client's details.

        This method displays a series of prompts to collect information required to modify a client's details.
        It allows the user to leave fields blank if they do not wish to modify them.
        It ensures that the input provided by the user is valid and within specified limits.

        Returns:
            dict: A dictionary containing the modification data for the client.
        """
        modification_data = {}
        self.display_info_message("Leave blank any field you do not wish to modify")

        new_full_name = self.get_valid_input_with_limit("New full name (max 100 characters) or leave blank",
                                                        100, allow_blank=True)
        if new_full_name:
            modification_data["full_name"] = new_full_name

        new_email = self.get_valid_email(allow_blank=True)
        if new_email:
            modification_data["email"] = new_email

        new_phone = self.get_valid_input_with_limit("New phone number (max 20 characters) or leave blank",
                                                    20, allow_blank=True)
        if new_phone:
            modification_data["phone"] = new_phone

        new_company_name = self.get_valid_input_with_limit("New company name (max 100 characters) or leave blank",
                                                           100, allow_blank=True)
        if new_company_name:
            modification_data["company_name"] = new_company_name

        return modification_data

    def get_data_for_contract_modification(self) -> dict:
        """
        Prompt the user to provide information for modifying a contract.

        This method displays prompts to collect information required to modify a contract.
        It allows the user to leave fields blank if they do not wish to modify them.
        It ensures that the input provided by the user is valid.

        Returns:
            dict: A dictionary containing the modification data for the contract.
        """
        modification_data = {}
        self.display_info_message("Modifying contract..."
                                  "Please leave blank any field you do not wish to modify")

        new_total_amount = self.get_valid_decimal_input("Total Amount (e.g. 9999.99)", allow_blank=True)
        if new_total_amount:
            modification_data["total_amount"] = "{:.2f}".format(new_total_amount)

        new_amount_remaining = self.get_valid_decimal_input("Amount remaining (e.g. 9999.99)", allow_blank=True)
        if new_amount_remaining:
            modification_data["amount_remaining"] = "{:.2f}".format(new_amount_remaining)

        new_status = self.get_valid_choice("New status (Options: signed, not_signed)",
                                           choices=["signed", "not_signed"],
                                           allow_blank=True)
        if new_status:
            modification_data["status"] = new_status

        return modification_data

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
        """
        Prompts the user for information to add a new event.

        This method guides the user through providing information for a new event.
        It prompts for the client name, event name, client contact, start and end dates,
        location, number of attendees, and optional notes. It constructs and returns
        a dictionary containing the collected event data.

        Returns:
            dict: A dictionary containing the collected event data.
        """
        self.display_info_message("Please provide the following information for the new event")

        # Requesting information for the new event.
        client_name = self.get_valid_input_with_limit("Client Name", 100)
        name = self.get_valid_input_with_limit("Name", 255)
        client_contact = self.get_valid_input_with_limit("Client Contact", 1000)
        start_date = self.get_valid_start_date()
        end_date = self.get_valid_end_date(start_date)
        location = self.get_valid_input_with_limit("Location", 300)
        attendees = self.get_valid_input_positive_integer("Attendees")
        notes = click.prompt("Notes (optional)", default="", show_default=False).strip()

        # Construct a dictionary containing the collected event data
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

    def get_valid_input_positive_integer(self, prompt_text: str) -> int:
        """
        Prompts the user for a positive integer input.

        This method continuously prompts the user for an integer until a positive one is provided.
        It checks if the input can be converted to an integer and if it's greater than zero.
        Displays error messages for invalid input or non-positive integers.

        Args:
            prompt_text (str): The prompt text to be displayed to the user.

        Returns:
            int: The valid positive integer input.
        """
        while True:
            user_input_str = click.prompt(prompt_text, default="", show_default=False)
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
        """
        Prompts the user for a valid start date, ensuring it's in the future.

        This method continuously prompts the user for a start date until a valid one is provided.
        It checks if the input can be parsed into a datetime object and if it's in the future.
        Displays error messages for invalid input or start dates in the past.

        Returns:
            datetime: The valid start date.
        """

        # Loop to ensure valid input for the start date.
        while True:
            start_date_str = click.prompt("New start date (YYYY-MM-DD HH:MM)", default="", show_default=False)
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
        """
         Prompts the user for a valid end date, ensuring it's after the provided start date.

         This method continuously prompts the user for an end date until a valid one is provided.
         It checks if the input can be parsed into a datetime object and if it's after the start date.
         Displays error messages for invalid input or end dates before or equal to the start date.

         Args:
             start_date (datetime): The start date to compare the end date against.

         Returns:
             datetime: The valid end date.
         """

        # Loop to ensure valid input for the end date.
        while True:
            end_date_str = click.prompt("New end date (YYYY-MM-DD HH:MM)", default="", show_default=False)
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
        """
        Displays the details of an event in a formatted table.
        """

        console = Console()
        self.clear_screen()

        # Create a table to display event details.
        table = Table(title="Event Detail",
                      show_header=True,
                      header_style="bold blue",
                      show_lines=True)

        # Add columns to the table.
        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width=40)

        # Add rows to the table with event details.
        table.add_row("Event ID", str(event.id))
        table.add_row("Contract ID", str(event.contract.id))
        table.add_row("Client Name", event.client_name)
        table.add_row("Event Name", event.name)
        table.add_row("Client Contact", event.client_contact)
        table.add_row("Start Date", event.start_date.strftime("%Y-%m-%d %H:%M"))
        table.add_row("End Date", event.end_date.strftime("%Y-%m-%d %H:%M"))

        # Get the full name of the support contact or display "N/A" if there is no contact.
        support_contact_name = event.support_contact.get_full_name() if event.support_contact else "N/A"
        table.add_row("Support Contact", support_contact_name)
        table.add_row("Location", event.location)
        table.add_row("Attendees", str(event.attendees))
        table.add_row("Notes", event.notes or "N/A")

        # Print the table to the console, justifying the content to the center.
        console.print(table, justify="center")

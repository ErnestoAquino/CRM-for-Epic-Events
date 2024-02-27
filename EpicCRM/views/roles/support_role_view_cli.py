from datetime import datetime
from typing import Optional
from typing import List
from django.db.models.query import QuerySet
from django.utils.timezone import make_aware
from django.utils.timezone import get_default_timezone
from dateutil.parser import parse
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from rich.box import ROUNDED
from colorama import Fore
from colorama import Style

from crm.models import Collaborator
from crm.models import Client
from crm.models import Event

from views.base_view_cli import BaseViewCli


class SupportRoleViewCli(BaseViewCli):
    MENU_OPTIONS = [
        "1 - View the list of all clients.",
        "2 - View the list of all contracts.",
        "3 - View the list of all events.",
        "4 - View your assigned events.",
        "5 - Modify one of your assigned events.",
        "6 - Exit of CRM system."
    ]
    MENU_LIMIT = len(MENU_OPTIONS)

    def show_main_menu(self, collaborator: Collaborator) -> None:
        """
        Display the main menu of the CRM system.

        This method displays the main menu options to the user.
        It formats the menu options in a table and prints them to the console.

        Args:
            collaborator (Collaborator): The logged-in collaborator for whom the menu is being displayed.
        """
        self.clear_screen()
        console = Console()

        # Get the full name or username if the full name is not available.
        name_to_display = collaborator.get_full_name() or collaborator.username

        # Create a table for the menu options.
        table = Table(show_header=True,
                      header_style="bold magenta")

        table.add_column("Menu Options",
                         justify="left",
                         style="dim")

        # Add menu options to the table
        for option in self.MENU_OPTIONS:
            table.add_row(option)

        self.display_info_message(f"Welcome {name_to_display}.")
        self.display_info_message(f"What operation wold you like to perform?\n")

        # Print table (menu options)
        console.print(table)

    def get_user_menu_choice(self) -> int:
        """
        Prompt the user to choose an option from the main menu.
        Returns:
            int: The user's menu choice.
        """

        # Capture user choice
        choice = self.get_collaborator_choice(limit=self.MENU_LIMIT)

        return choice

    @staticmethod
    def display_list_events_for_collaborator(events_queryset: QuerySet, collaborator: Collaborator) -> None:
        # Create console instance.
        console = Console()
        name_to_display = collaborator.get_full_name() or collaborator.username

        # Create table
        table = Table(title=f"Assigned Events for {name_to_display}.",
                      show_header=True,
                      header_style="bold magenta",
                      expand=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Contract ID", style="dim", width=12)
        table.add_column("Name", style="dim", width=12)
        table.add_column("Client Name", style="dim", width=20)
        table.add_column("Start Date", style="dim", width=20)
        table.add_column("End Date", style="dim", width=20)
        table.add_column("Location", style="dim", width=25)
        table.add_column("Attendees", justify="right", style="dim", width=12)
        table.add_column("Notes", style="dim", width=30)

        # Fill the table with events' data
        for event in events_queryset:
            event_name = event.name if event.name else "No Named"
            contract_id = str(event.contract.id) if event.contract else "No Contract"
            client_name = event.client_name
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
                start_date,
                end_date,
                location,
                attendees,
                notes
            )

        # Print the table using Rich
        console.print(table)

    def get_data_for_event_modification(self) -> dict:
        """
        Collect data from the user for modifying an event.

        This method prompts the user to enter new data for modifying different fields of an event.
        The user can leave a field blank if they do not wish to modify it.
        The method collects data such as the new name, client name, client contact, location, notes, attendees,
        start date, and end date. It validates the input for each field.

        Returns:
            dict: A dictionary containing the modified data for the event.
        """
        modification_data = {}

        self.display_info_message("Leave blank any field you do not wish to modify.")

        new_name = self.get_valid_input_with_limit("New Name (or leave blank)", 100, allow_blank=True)
        if new_name:
            modification_data["name"] = new_name

        new_client_name = self.get_valid_input_with_limit("New Client Name (or leave blank)", 100, allow_blank=True)
        if new_client_name:
            modification_data["client_name"] = new_client_name

        new_client_contact = self.get_valid_input_with_limit("New contact information (or leave blank)", 250,
                                                             allow_blank=True)
        if new_client_contact:
            modification_data["client_contact"] = new_client_contact

        new_location = self.get_valid_input_with_limit("New Location (or leave blank)", 250, allow_blank=True)
        if new_location:
            modification_data["location"] = new_location

        new_notes = self.get_valid_input_with_limit("New Notes (or leave blank)", 500, allow_blank=True)
        if new_notes:
            modification_data["notes"] = new_notes

        new_attendees = self.get_valid_integer_input("New Attendees (or leave blank)", allow_blank=True)
        if new_attendees:
            modification_data["attendees"] = new_attendees

        new_start_date = self.get_valid_start_date(allow_blank=True)
        if new_start_date:
            modification_data["start_date"] = new_start_date
            new_end_date = self.get_valid_end_date(new_start_date, allow_blank=True)
            if new_end_date:
                modification_data["end_date"] = new_end_date

        return modification_data

    def get_valid_integer_input(self, prompt_text: str, allow_blank: bool = False) -> Optional[int]:
        """
        Prompts the user for a valid integer input.

        This method prompts the user with a specified prompt text to enter an integer number.
        It validates the input and returns the integer value entered by the user.
        If 'allow_blank' is set to True, it allows the input to be empty (None).

        Args:
            prompt_text (str): The prompt text to display to the user.
            allow_blank (bool, optional): Whether to allow blank input (default is False).

        Returns:
            Optional[int]: The validated integer value entered by the user, or None if input is blank.
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
                # Convert input to int and check if it's an integer
                value = int(user_input)
                return value
            except ValueError:
                # Handle non-numeric input
                self.display_error_message("Please enter a valid integer number (e.g. 12345)")
                continue

    def get_valid_start_date(self, allow_blank: bool = False) -> Optional[datetime]:
        """
        Prompts the user for a valid start date, ensuring it's in the future or optionally allows blank input.

        This method continuously prompts the user for a start date until a valid one is provided or
        allows for a blank input if allow_blank is True.
        It checks if the input can be parsed into a datetime object and if it's in the future.
        Displays error messages for invalid input or start dates in the past.

        Args:
            allow_blank (bool): If True, allows the method to return None for blank inputs.

        Returns:
            datetime or None: The valid start date, or None if blank input is allowed and chosen.
        """

        while True:
            start_date_str = click.prompt("New start date (YYYY-MM-DD HH:MM)", default="", show_default=False)

            # Allows blank input if allow_blank is True and the input is blank.
            if allow_blank and start_date_str.strip() == "":
                return None

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

    def get_valid_end_date(self, start_date: datetime, allow_blank: bool = False) -> Optional[datetime]:
        """
        Prompts the user for a valid end date,
        ensuring it's after the provided start date or optionally allows blank input.

        This method continuously prompts the user for an end date until a valid one is provided or
        allows for a blank input if allow_blank is True.
        It checks if the input can be parsed into a datetime object and if it's after the start date.
        Displays error messages for invalid input or end dates before or equal to the start date.

        Args:
            start_date (datetime): The start date to compare the end date against.
            allow_blank (bool): If True, allows the method to return None for blank inputs.

        Returns:
            datetime or None: The valid end date, or None if blank input is allowed and chosen.
        """

        while True:
            end_date_str = click.prompt("New end date (YYYY-MM-DD HH:MM)", default="", show_default=False)

            # Allows blank input if allow_blank is True and the input is blank.
            if allow_blank and end_date_str.strip() == "":
                return None

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
                self.display_error_message("End date must be after the start date. Please try again.")
                continue

            # Returns the valid end date.
            return aware_end_date

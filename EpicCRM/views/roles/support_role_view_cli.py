from datetime import datetime
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

    def display_events_for_selection(self, events_queryset: QuerySet) -> None:
        # Create console instance
        console = Console()

        # Create table
        table = Table(title="List of Available Events", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Name", style="dim", width=20)
        table.add_column("Client Name", style="dim", width=20)

        # Fill the table with events data
        for event in events_queryset:
            event_name = event.name if event.name else "No Name"
            client_name = event.client_name

            table.add_row(
                str(event.id),
                event_name,
                client_name
            )

        # Print the table using Rich
        console.print(table)

    def display_event_details(self, event: Event) -> None:
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

    def prompt_for_event_modification(self) -> dict:
        modifications = {}
        self.display_info_message("Leave blank any field you do not wish to modify.")

        new_name = click.prompt("New name for event", default="", show_default=False)
        if new_name:
            modifications["name"] = new_name

        new_client_name = click.prompt("New client name", default="", show_default=False)
        if new_client_name:
            modifications["client_name"] = new_client_name

        new_client_contact = click.prompt("New client contact", default="", show_default=False)
        if new_client_contact:
            modifications["client_contact"] = new_client_contact

        new_location = click.prompt("New location", default="", show_default=False)
        if new_location:
            modifications["location"] = new_location

        new_notes = click.prompt("New notes", default="", show_default=False)
        if new_notes:
            modifications["notes"] = new_notes

        # Request new attendees
        while True:
            new_attendees_str = click.prompt("New number of attendees", default="", show_default=False)
            if not new_attendees_str:
                break  # Exit the loop if the user leaves the field blank
            try:
                new_attendees = int(new_attendees_str)
                if new_attendees <= 0:
                    self.display_error_message("Number of attendees cannot be negative or zero. Please try again.")
                    continue
                modifications["attendees"] = new_attendees
                break  # End the loop after processing a valid number of attendees
            except ValueError:
                self.display_error_message("Please enter a valid integer for the number of attendees.")

        # Request new start date
        while True:
            new_start_date_str = click.prompt("New start date (YYYY-MM-DD HH:MM)", default="", show_default=False)
            if not new_start_date_str:
                break  # Exit the loop if the user leaves the field blank
            try:
                naive_start_date = parse(new_start_date_str)
                if naive_start_date < datetime.now():
                    self.display_error_message("Start date must be in the future. Please try again.")
                    continue
                # Making date/time "aware" to comply with Django and avoid timezone warnings, ensuring correct
                # timezone handling.
                aware_start_date = make_aware(naive_start_date, get_default_timezone())
                modifications["start_date"] = aware_start_date
                break  # End the loop after processing a valid start date
            except ValueError:
                self.display_error_message("Invalid date format. Please use YYYY-MM-DD HH:MM.")

        # Request a new end date
        while True:
            new_end_date_str = click.prompt("New end date (YYYY-MM-DD HH:MM)", default="", show_default=False)
            if not new_end_date_str:
                break  # Exit the loop if the user leaves the field blank
            try:
                naive_end_date = parse(new_end_date_str)
                # Ensure that the new end date is after the new start date (if modified)
                if "start_date" in modifications:
                    # Making date/time "aware" to comply with Django and avoid timezone warnings.
                    aware_end_date = make_aware(naive_end_date, get_default_timezone())
                    if aware_end_date <= modifications["start_date"]:
                        self.display_error_message("End date must be after start date. Please try again.")
                        continue
                    modifications["end_date"] = aware_end_date
                    break  # End the loop after processing a valid end date
            except ValueError:
                self.display_error_message("Invalid date format. Please use YYYY-MM-DD HH:MM.")

        return modifications

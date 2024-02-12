from datetime import datetime
from django.db.models.query import QuerySet
from django.utils.timezone import make_aware
from django.utils.timezone import get_default_timezone
from dateutil.parser import parse
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
import rich.box
from rich.box import ROUNDED
from colorama import Fore
from colorama import Style

from crm.models import Collaborator
from crm.models import Client
from crm.models import Event


class SupportRoleViewCli:
    MENU_OPTIONS = [
        "1 - View the list of all clients.",
        "2 - View the list of all contracts.",
        "3 - View the list of all events.",
        "4 - View your assigned events.",
        "5 - Modify one of your assigned events.",
        "6 - Exit of CRM system."
    ]
    MENU_LIMIT = len(MENU_OPTIONS)

    def show_main_menu(self, collaborator: Collaborator) -> int:
        click.clear()

        # Get the full name or username if the full name is not available.
        name_to_display = collaborator.get_full_name() or collaborator.username

        click.echo(f"{Fore.GREEN} Welcome {name_to_display}.{Style.RESET_ALL}")
        click.echo("What operation would you like to perform?\n")

        # Print menu options
        for option in self.MENU_OPTIONS:
            click.echo(f"{Fore.YELLOW}{option}{Style.RESET_ALL}")

        # Capture user choice
        choice = self.get_collaborator_choice(limit=self.MENU_LIMIT)

        return choice

    @staticmethod
    def get_collaborator_choice(limit: int) -> int:
        while True:
            choice = click.prompt("Please choose an option", type=int)
            if 1 <= choice <= limit:
                return choice
            else:
                click.secho("Invalid option. Please try again.", fg="red")

    def display_list_of_clients(self, clients_queryset: QuerySet) -> None:
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
        for client in clients_queryset:
            table.add_row(
                client.full_name,
                client.email,
                client.phone,
                client.company_name,
                client.creation_date.strftime("%Y-%m-%d %H:%M")
            )

        # Print the table using Rich
        console.print(table)

    def display_list_of_contracts(self, contracts_queryset: QuerySet) -> None:
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
        for contract in contracts_queryset:
            client_name = contract.client.full_name if contract.client else "No Client Assigned"
            sales_contact_name = contract.sales_contact.get_full_name() if contract.sales_contact else ("No Contact "
                                                                                                        "Assigned")
            total_amount = f"${contract.total_amount:.2f}"
            amount_remaining = f"${contract.amount_remaining:.2f}"
            creation_date = contract.creation_date.strftime("%Y-%m-%d %H:%M")

            # Use get_status_display() to get the human-readable version of a ChoiceField
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

    def display_list_of_events(self, events_queryset: QuerySet) -> None:
        # Create console instance.
        console = Console()

        # Create table
        table = Table(title="List of all Events", show_header=True, header_style="bold magenta", expand=True)
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
        for event in events_queryset:
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
        table = Table(title="Event Detail", show_header=True, header_style="bold blue")
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

    @staticmethod
    def display_error_message(error_message: str) -> None:
        console = Console()
        error_text = Text(error_message, style="bold red")
        console.print(error_text)

    @staticmethod
    def display_info_message(info_message: str) -> None:
        console = Console()
        info_text = Text(info_message, style="bold green")
        console.print(info_text)

    @staticmethod
    def display_message(message: str) -> None:
        console = Console()
        message_text = Text(message, style="bold magenta")
        console.print(message_text)

    @staticmethod
    def ask_user_if_continue():
        while True:
            response = click.prompt("Do you want to perform another operation? (yes/no)", type=str).lower()
            if response == "yes":
                return True
            elif response == "no":
                return False
            else:
                click.secho("Invalid response. Please enter 'yes' or 'no'.", fg="red")

    @staticmethod
    def clear_screen() -> None:
        click.clear()

    @staticmethod
    def prompt_for_get_event_id(events_id: [int]) -> int:
        while True:
            event_id = click.prompt("Please enter the ID of event you wish to modify", type=int)
            if event_id in events_id:
                return event_id
            else:
                click.secho("Invalid event ID. Please choose from the list", fg="red")

    @staticmethod
    def prompt_for_event_selection(events: QuerySet[Event]) -> Event:
        event_ids = [event.id for event in events]
        event_id = click.prompt("Please enter the ID of event you wish to modify", type=int)
        if event_id in event_ids:
            return event_id
        else:
            click.secho("Invalid event ID. Please choose from the list", fg="red")

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

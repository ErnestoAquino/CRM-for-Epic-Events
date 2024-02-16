from django.db.models.query import QuerySet
import click
from rich.box import ROUNDED
from rich.console import Console
from rich.table import Table
from rich.text import Text


class BaseViewCli:

    def ask_user_if_continue(self) -> bool:
        while True:
            response = click.prompt("Do you want to perform another operation? (yes/no)", type=str).lower()
            if response == "yes":
                return True
            elif response == "no":
                return False
            else:
                self.display_error_message("Invalid response. Please enter 'yes' or 'no'.")

    def get_collaborator_choice(self, limit: int) -> int:
        while True:
            choice = click.prompt("Please choose an option", type=int)
            if 1 <= choice <= limit:
                return choice
            else:
                self.display_error_message("Invalid option. Please try again.")

    def prompt_for_selection_by_id(self, ids: [int], model_name: str) -> int:
        # Ask the user to choose an ID
        while True:
            selected_id = click.prompt(f"Please enter the ID of the {model_name} you wish to modify.", type=int)
            if selected_id in ids:
                return selected_id
            else:
                self.display_error_message(f"Invalid {model_name} ID. Please choose of the list.")

    @staticmethod
    def clear_screen() -> None:
        click.clear()

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
    def display_warning_message(message: str) -> None:
        console = Console()
        message_text = Text(message, style="bold yellow")
        console.print(message_text)

    @staticmethod
    def display_list_of_events(events_queryset: QuerySet) -> None:
        # Create console instance.
        console = Console()

        # Create table
        table = Table(title="List of all Events",
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

    @staticmethod
    def display_list_of_clients(clients_queryset: QuerySet) -> None:
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

    @staticmethod
    def display_list_of_contracts(contracts_queryset: QuerySet) -> None:
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

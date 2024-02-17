import re
import click
from views.base_view_cli import BaseViewCli
from rich.console import Console
from rich.table import Table
from colorama import Fore, Style
from django.db.models.query import QuerySet

from crm.models import Collaborator


class ManagementRoleViewCli(BaseViewCli):
    def get_data_for_create_collaborator(self) -> dict:

        first_name = self.get_valid_input_with_limit("First Name", 50)
        last_name = self.get_valid_input_with_limit("Last Name", 50)
        username = self.get_valid_input_with_limit("Username", 50)
        password = self.get_valid_password()
        email = self.get_valid_email()
        role = self.get_valid_role_for_collaborator()
        employee_number = self.get_valid_input_with_limit("Employee Number", 50)

        collaborator_data = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "password": password,
            "email": email,
            "role_name": role,
            "employee_number": employee_number
        }

        return collaborator_data

    def get_valid_role_for_collaborator(self, allow_blank: bool = False) -> str:
        roles_choices = ['management', 'sales', 'support']
        role_prompt = "Role (management, sales, support)"

        while True:
            role = click.prompt(role_prompt, type=str, default="", show_default=True).strip().lower()

            if allow_blank and role == "":
                return role

            if not role:
                self.display_warning_message("Role cannot be empty.")
                continue

            if role not in roles_choices:
                self.display_error_message(f"Invalid role. Please enter a valid role: {', '.join(roles_choices)}.")
                continue

            return role

    def get_valid_password(self) -> str:
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

        password_instructions = ("Password must contain at least one uppercase letter, one lowercase letter, "
                                 "one number, and be at least 8 characters long.")

        while True:
            password = click.prompt(Fore.YELLOW + "Password" + Style.RESET_ALL, hide_input = True).strip()
            if not password:
                self.display_warning_message("Password cannot be empty.")
                continue

            if not re.fullmatch(password_regex, password):
                self.display_error_message(f"Invalid password format. {password_instructions}")
                continue

            confirm_password = click.prompt(Fore.YELLOW + "Confirm password" + Style.RESET_ALL, hide_input = True)
            if password != confirm_password:
                self.display_error_message("Passwords do not match. Please try again.")
                continue

            return password

    def display_collaborator_details(self, collaborator: Collaborator) -> None:
        self.clear_screen()
        console = Console()

        # Create a table to display collaborator details
        table = Table(title = "Collaborator Detail", show_header = True, header_style = "bold blue", show_lines = True)
        table.add_column("Field", style = "dim", width = 20)
        table.add_column("Value", width = 40)

        # Add rows to the table with collaborator details
        table.add_row("Collaborator ID", str(collaborator.id))
        table.add_row("First Name", collaborator.first_name)
        table.add_row("Last Name", collaborator.last_name)
        table.add_row("Username", collaborator.username)
        table.add_row("Email", collaborator.email)
        table.add_row("Employee Number", collaborator.employee_number)
        table.add_row("Role", collaborator.role.name if collaborator.role else "N/A")

        # Print the table
        console.print(table, justify = "center")

    def display_collaborators_for_selection(self, collaborators: QuerySet[Collaborator]) -> None:
        # Create console instance
        console = Console()

        # Create table
        table = Table(title="List of Available Collaborators", show_header=True, header_style="bold magenta",
                      expand=True, show_lines=True)
        table.add_column("Collaborator ID", style="dim", width=15)
        table.add_column("Full Name", width=25)

        # Fill the table with collaborators data
        for collaborator in collaborators:
            full_name = f"{collaborator.first_name} {collaborator.last_name}"

            table.add_row(
                str(collaborator.id),
                full_name
            )

        # Print the table using Rich
        console.print(table)

    def get_data_for_modify_collaborator(self) -> dict:
        self.display_info_message("Modifying collaborator: {collaborator.username}. "
                                  "Leave blank any field you do not wish to modify.")

        modification_data = {}

        first_name = self.get_valid_input_with_limit("New First Name (or leave blank)", 50, allow_blank=True)
        if first_name:
            modification_data["first_name"] = first_name

        last_name = self.get_valid_input_with_limit("New Last Name (or leave blank)", 50, allow_blank=True)
        if last_name:
            modification_data["last_name"] = last_name

        email = self.get_valid_email(allow_blank=True)
        if email:
            modification_data["email"] = email

        role = self.get_valid_role_for_collaborator(allow_blank = True)
        if role:
            modification_data["role_name"] = role

        employee_number = self.get_valid_input_with_limit("New Employee Number (or leave blank)", 50, allow_blank=True)
        if employee_number:
            modification_data["employee_number"] = employee_number

        return modification_data

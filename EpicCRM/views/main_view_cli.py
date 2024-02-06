import click
from colorama import Fore


class MainViewCLI:
    @staticmethod
    def prompt_login():
        click.clear()
        click.secho("Welcome to Epic Events CRM!", fg="blue", bold=True)
        click.secho("Please log in...", fg="blue", bold=True)
        username = click.prompt(Fore.YELLOW + "Username: ")
        password = click.prompt(Fore.YELLOW + "Password: ", hide_input=True)

        return {
            "username": username,
            "password": password
        }

    @staticmethod
    def get_data_for_register_new_collaborator():
        click.clear()
        click.secho("Registering new collaborator...", fg="green", bold=True)

        first_name = click.prompt(Fore.YELLOW + "First Name")
        last_name = click.prompt(Fore.YELLOW + "Last Name")
        username = click.prompt(Fore.YELLOW + "Username")
        password = click.prompt(Fore.YELLOW + "Password", hide_input=True)
        email = click.prompt(Fore.YELLOW + "Email")
        role_name = click.prompt(Fore.YELLOW + "Rol (management, sales, support")
        employee_number = click.prompt(Fore.YELLOW + "Employee Number")

        return {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'password': password,
            'email': email,
            'role_name': role_name,
            'employee_number': employee_number
        }

    @staticmethod
    def print_message(message: str, color: str = "white"):
        if color == "green":
            click.secho(message, fg="green", bold=True)
        elif color == "red":
            click.secho(message, fg="red", bold=True)
        elif color == "yellow":
            click.secho(message, fg="yellow", bold=True)
        else:
            click.secho(message, fg="white", bold=True)

    def show_main_menu(self, collaborator):
        click.secho(f"Welcome to CRM Epic Events {collaborator.username}.")

        # Basic options for all collaborators
        options = {
            "view_contracts": "View all contracts",
            "view_events": "View all events",
            "view_clients": "View all clients"
        }

        # Add the option to manage collaborators iif the user has permission.
        if collaborator.has_perm("crm.manage_collaborators"):
            options = {"manage_collaborators": "Manage Collaborators", **options}

        # Display the numbered options
        for i, (code, option) in enumerate(options.items(), start=1):
            click.secho(f"{i}. {option}", fg="green")

        # Capture the user's choice
        choice = self.get_collaborator_choice(len(options))

        # Get the option code based in the choice
        option_code = list(options.keys())[choice - 1]

        return option_code

    @staticmethod
    def get_collaborator_choice(limit) -> int:
        while True:
            choice = click.prompt("Please choose an option", type=int)
            if 1 <= choice <= limit:
                return choice
            else:
                click.secho("Invalid option. Please try again.", fg="red")

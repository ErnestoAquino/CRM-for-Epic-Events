import click
from colorama import Fore
from views.base_view_cli import BaseViewCli


class MainViewCLI(BaseViewCli):
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

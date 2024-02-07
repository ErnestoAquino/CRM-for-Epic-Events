import click
from colorama import Fore
from colorama import Style

from crm.models import Collaborator


class SupportRoleViewCli:
    MENU_OPTIONS = [
        "1 - View the list of all clients.",
        "2 - View the list of all contracts.",
        "3 - View the list of all events.",
        "4 - View your assigned events.",
        "5 - Modify one of your assigned events."
    ]
    MENU_LIMIT = len(MENU_OPTIONS)

    def show_main_menu(self, collaborator: Collaborator):
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
import click
from colorama import Fore


class ViewCLI:
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
        click.secho("Registering new collaborator...", fg = "green", bold = True)

        first_name = click.prompt(Fore.YELLOW + "First Name")
        last_name = click.prompt(Fore.YELLOW + "Last Name")
        username = click.prompt(Fore.YELLOW + "Username")
        password = click.prompt(Fore.YELLOW + "Password", hide_input = True)
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

    @staticmethod
    def show_main_menu(user):
        if user.has_perm("crm.manage_collaborators"):
            click.secho("Menu for manage collaborators", fg="green")
        else:
            click.secho("You do not have permission to manage collaborators", fg="red")
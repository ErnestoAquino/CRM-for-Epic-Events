import click
from colorama import Fore


class ViewCLI:
    def prompt_login(self):
        pass

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
            click.secho(message, fg = "green", bold = True)
        elif color == "red":
            click.secho(message, fg = "red", bold = True)
        elif color == "yellow":
            click.secho(message, fg = "yellow", bold = True)

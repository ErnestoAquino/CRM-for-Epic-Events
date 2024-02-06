from typing import Optional
from django.core.exceptions import ValidationError
from crm.models import Collaborator
from services.services_crm import ServicesCRM
from views.main_view_cli import MainViewCLI


class MainControllerCRM:
    def __init__(self):
        self.crm_services = ServicesCRM()
        self.view_cli = MainViewCLI()

    def create_collaborator(self):
        data = self.view_cli.get_data_for_register_new_collaborator()

        try:
            self.crm_services.register_collaborator(**data)
            self.view_cli.print_message("User registered successfully", "green")
        except ValidationError as e:
            self.view_cli.print_message(f"Error: {e}", "red")
        except ValueError as e:
            self.view_cli.print_message(f"Error: {e}", "red")

    def authenticate_collaborator(self) -> Optional[Collaborator]:
        login_data = self.view_cli.prompt_login()
        try:
            user = self.crm_services.authenticate_collaborator(**login_data)
            self.view_cli.print_message("Logged in successfully!", "green")
            return user
        except ValidationError as e:
            self.view_cli.print_message(f"Login failed: {e}", "red")
            return None

    def present_main_menu(self, user):
        self.view_cli.show_main_menu(user)

    def start(self):
        collaborator = self.authenticate_collaborator()
        if collaborator is None:
            self.view_cli.print_message("We encountered a problem during the process. Please try again.", "red")
            return

        option_code = self.view_cli.show_main_menu(collaborator)
        match option_code:
            case "manage_collaborators":
                print("call  ManagementCollaboratorsControllerCRM")
            case "view_contracts":
                print("call  show_contacts")
            case "view_clients":
                print("call present_clients")
            case "view_events":
                print("call present_events")
            case _: self.view_cli.print_message(f"Option Code: '{option_code}' not recognized", "red")

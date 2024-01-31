from django.core.exceptions import ValidationError
from services.ServicesCRM import ServicesCRM
from views.ViewCLI import ViewCLI


class ControllerCRM:
    def __init__(self):
        self.crm_services = ServicesCRM()
        self.view_cli = ViewCLI()

    def create_collaborator(self):
        data = self.view_cli.get_data_for_register_new_collaborator()

        try:
            self.crm_services.register_collaborator(**data)
            self.view_cli.print_message("User registered successfully", "green")
        except ValidationError as e:
            self.view_cli.print_message(f"Error: {e}", "red")
        except ValueError as e:
            self.view_cli.print_message(f"Error: {e}", "red")

from typing import Optional
from django.core.exceptions import ValidationError

from crm.models import Collaborator
from crm.models import Role

from controllers.roles.support_role_controller import SupportRoleController
from controllers.roles.sales_role_controller import SalesRoleController
from controllers.roles.management_role_controller import ManagementRoleController

from controllers.models.client_controller import ClientController
from controllers.models.contract_controller import ContractController
from controllers.models.event_controller import EventController

from services.services_crm import ServicesCRM

from views.main_view_cli import MainViewCLI
from views.roles.support_role_view_cli import SupportRoleViewCli
from views.roles.sales_role_view_cli import SalesRoleViewCli
from views.roles.management_role_view_cli import ManagementRoleViewCli


class MainControllerCRM:
    def __init__(self):
        self.crm_services = ServicesCRM()
        self.view_cli = MainViewCLI()

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
        services = ServicesCRM()

        # Verify that the collaborator objects exists.
        if collaborator is None:
            self.view_cli.print_message("We encountered a problem during the process. Please try again.", "red")
            return

        # Verify that collaborator's role in not null.
        if collaborator.role is not None:
            role_name = collaborator.role.name
        else:
            self.view_cli.print_message("Your account does not have a role assigned", "yellow")
            return

        match role_name:
            case "support":
                client_controller = ClientController(collaborator, services)
                contract_controller = ContractController(collaborator, services)
                event_controller = EventController(collaborator, services)
                view_cli = SupportRoleViewCli()

                support_role_controller = SupportRoleController(collaborator,
                                                                client_controller,
                                                                contract_controller,
                                                                event_controller,
                                                                view_cli)
                support_role_controller.start()
            case "sales":
                view_cli = SalesRoleViewCli()
                sales_role_controller = SalesRoleController(collaborator,
                                                            self.crm_services,
                                                            view_cli)
                sales_role_controller.start()
            case "management":
                view_cli = ManagementRoleViewCli()
                management_role_controller = ManagementRoleController(collaborator,
                                                                      self.crm_services,
                                                                      view_cli)
                management_role_controller.start()
            case _:
                self.view_cli.print_message("Your role does not have specific task assigned.", "yellow")

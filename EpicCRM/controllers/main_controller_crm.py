from typing import Optional
from django.core.exceptions import ValidationError

from crm.models import Collaborator
from crm.models import Role

from controllers.roles.support_role_controller import SupportRoleController
from controllers.roles.sales_role_controller import SalesRoleController
from controllers.roles.management_role_controller import ManagementRoleController

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
        """
        Authenticate a collaborator using the provided username and password.

        This method prompts the user to enter their username and password
        through the `prompt_login` method. It then attempts to authenticate
        the collaborator using the CRM services. If authentication is successful,
        it displays a success message and returns the authenticated user.
        If authentication fails due to validation error, it displays an error message
        and returns None.

        Returns:
            Optional[Collaborator]: The authenticated collaborator if successful, else None.
        """

        login_data = self.view_cli.prompt_login()
        try:
            # Attempt to authenticate the collaborator
            user = self.crm_services.authenticate_collaborator(**login_data)
            self.view_cli.display_info_message("Logged in successfully!")
            return user
        except ValidationError as e:
            # Display an error message if authentication fails due to validation error
            self.view_cli.display_error_message(f"Login failed: {e}")
            return None

    def start(self):
        """
        Start the application after authenticating the collaborator.

        This method first authenticates the collaborator using the `authenticate_collaborator` method.
        It then verifies that the collaborator object exists. If not, it returns.
        Based on the role of the collaborator, it initializes the appropriate role-specific view CLI and controller,
        and starts the corresponding controller.
        """
        collaborator = self.authenticate_collaborator()

        # Verify that the collaborator objects exist.
        if collaborator is None:
            return

        # Verify that collaborator's role is not null.
        if collaborator.role is not None:
            role_name = collaborator.role.name
        else:
            self.view_cli.display_warning_message("Your account does not have a role assigned")
            return

        match role_name:
            case "support":
                view_cli = SupportRoleViewCli()
                support_role_controller = SupportRoleController(collaborator, self.crm_services, view_cli)
                support_role_controller.start()
            case "sales":
                view_cli = SalesRoleViewCli()
                sales_role_controller = SalesRoleController(collaborator, self.crm_services, view_cli)
                sales_role_controller.start()
            case "management":
                view_cli = ManagementRoleViewCli()
                management_role_controller = ManagementRoleController(collaborator, self.crm_services, view_cli)
                management_role_controller.start()
            case _:
                self.view_cli.display_warning_message("Your role does not have specific task assigned.")

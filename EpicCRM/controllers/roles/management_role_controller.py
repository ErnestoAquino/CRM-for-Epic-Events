from typing import Optional
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.db.models.query import QuerySet
from crm.models import Collaborator
from services.services_crm import ServicesCRM
from views.roles.management_role_view_cli import ManagementRoleViewCli


class ManagementRoleController:
    MAIN_MENU_OPTIONS = [
        "1 - Create, update, and delete collaborators in the CRM system.",
        "2 - Create and modify all contracts.",
        "3 - Filter and display events, for example, show all events without an assigned 'support' contact.",
        "4 - Assign or change the 'support' collaborator associated with an event.",
        "5 - View the list of all clients.",
        "6 - View the list of all contracts.",
        "7 - View the list of all events.",
        "8 - Exit the CRM system."
    ]

    SUB_MENU_MANAGE_COLLABORATORS = [
        "1 - Create  a collaborator in the CRM system.",
        "2 - Update a collaborator in the CRM system.",
        "3 - Delete a collaborator in the CRM system",
        "4 - Return to main menu"
    ]

    def __init__(self, collaborator: Collaborator,
                 services_crm: ServicesCRM,
                 view_cli: ManagementRoleViewCli):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli

    def start(self):
        name_to_display = self.collaborator.get_full_name() or collaborator.username

        # Shows the main menu to the collaborator
        self.view_cli.show_menu(name_to_display, self.MAIN_MENU_OPTIONS)

        # captures their choice.
        choice = self.view_cli.get_collaborator_choice(limit=len(self.MAIN_MENU_OPTIONS))

        match choice:
            case 1:
                # Create, update, and delete collaborators in the CRM system.
                self.manage_collaborators()
            case 2:
                # TODO: Create and modify all contracts.
                pass
            case 3:
                # TODO: Filter and display events, for example, show all events without an assigned 'support' contact.
                pass
            case 4:
                # TODO: Assign or change the 'support' collaborator associated with an event.
                pass
            case 5:
                # TODO: View the list of all clients.
                pass
            case 6:
                # TODO:View the list of all contracts.
                pass
            case 7:
                # TODO: View the list of all events.
                pass
            case 8:
                #  Exit the CRM system.
                self.exit_of_crm_system()
                return
            case _:
                self.view_cli.display_error_message("Invalid option selected. Please try again.")
                self.start()

        # Asks the collaborator if they want to continue using the system.
        continue_operation = self.view_cli.ask_user_if_continue()

        if not continue_operation:
            # Exits the CRM system if the collaborator chooses not to continue.
            self.exit_of_crm_system()
            return

        # Restarts the start method to prompt the collaborator for another choice.
        self.start()

    # ============================== 1 - Manage Collaborators.   =======================================================
    def manage_collaborators(self) -> None:
        self.view_cli.clear_screen()

        # Check if the collaborator has the "manage_collaborator" permission which allows CRUD operations on
        # collaborators.
        if not self.collaborator.has_perm("crm.manage_collaborators"):
            self.view_cli.display_error_message("You do not have permission to manage collaborators.")
            return

        # Shows the sub menu for manage collaborators
        self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_MANAGE_COLLABORATORS)

        # captures their choice.
        choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_MANAGE_COLLABORATORS))

        match choice:
            case 1:
                # Create  a collaborator in the CRM system
                self.process_collaborator_creation()
            case 2:
                #  Update a collaborator in the CRM system
                self.process_collaborator_modification()
            case 3:
                #  Delete a collaborator in the CRM system
                self.process_collaborator_removal()
            case 4:
                # Return to main menu
                self.start()
            case _:
                self.view_cli.display_info_message("Invalid option selected. Please try again.")
                return

    def process_collaborator_creation(self) -> None:
        while True:
            self.view_cli.clear_screen()
            self.view_cli.display_info_message("Registering new collaborator...")
            data_collaborator = self.view_cli.get_data_for_create_collaborator()

            try:
                collaborator = self.services_crm.register_collaborator(**data_collaborator)
                self.view_cli.clear_screen()
                self.view_cli.display_collaborator_details(collaborator)
                self.view_cli.display_info_message("User registered successfully!")
                break
            except ValidationError as e:
                self.view_cli.display_error_message(str(e))
                continue_operation = self.view_cli.get_user_confirmation("Do you want try again?")
                if not continue_operation:
                    break
            except Exception as e:
                self.view_cli.display_error_message(str(e))
                break

    def process_collaborator_modification(self) -> None:
        self.view_cli.clear_screen()

        try:
            collaborators = self.services_crm.get_all_non_superuser_collaborators()
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database, please try again later.")
            return
        except Exception as e:
            self.view_cli.display_error_message(f"{e}")
            return

        if not collaborators:
            self.view_cli.display_info_message("There are no collaborators available to display.")
            return

        selected_collaborator = self.get_collaborator_for_modification(collaborators)
        if not selected_collaborator:
            self.view_cli.display_error_message("We couldn't find the collaborator. Please try again later.")
            return

        self.view_cli.display_collaborator_details(selected_collaborator)
        collaborator_data = self.view_cli.get_data_for_modify_collaborator()

        # Checks if no modifications were provided.
        if not collaborator_data:
            # Informs the user that no modifications were made and exits.
            self.view_cli.display_info_message("No modifications were made.")
            return

        try:
            collaborator_modify = self.services_crm.modify_collaborator(selected_collaborator, collaborator_data)
        except ValidationError as e:
            self.view_cli.display_error_message(str(e))
            return
        except DatabaseError:
            self.view.display_error_message("I encountered a problem with the database, please try again later.")
            return
        except Exception as e:
            self.view_cli.display_error_message(str(e))
            return
        self.view_cli.display_collaborator_details(collaborator_modify)
        self.view_cli.display_info_message("The collaborator has been modified successfully.")

    def get_collaborator_for_modification(self, collaborators: QuerySet[Collaborator]) -> Optional[Collaborator]:
        self.view_cli.clear_screen()
        self.view_cli.display_collaborators_for_selection(collaborators)
        collaborators_ids = [collaborator.id for collaborator in collaborators]
        selected_collaborator_id = self.view_cli.prompt_for_selection_by_id(collaborators_ids, "Collaborator")

        selected_collaborator = next((collaborator for collaborator in collaborators
                                      if collaborator.id == selected_collaborator_id), None)

        return selected_collaborator

    def process_collaborator_removal(self) -> None:
        pass

    # ============================== 9 - Exit the CRM system.    =======================================================
    def exit_of_crm_system(self) -> None:
        self.view_cli.clear_screen()
        self.view_cli.display_info_message("Thank you for using CRM Events, until next time!")

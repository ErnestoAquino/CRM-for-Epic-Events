from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db.models.query import QuerySet

from crm.models import Collaborator
from crm.models import Event
from crm.models import Contract
from crm.models import Client
from crm.models import Role


class ServicesCRM:
    @staticmethod
    def authenticate_collaborator(username: str, password: str):
        user = authenticate(username=username, password=password)
        if user is not None:
            return user
        else:
            raise ValidationError("Incorrect username or password")

    @staticmethod
    def register_collaborator(first_name: str,
                              last_name: str,
                              username: str,
                              password: str,
                              email: str,
                              role_name: str,
                              employee_number: str):

        # Check if the username is already in use.
        if Collaborator.objects.filter(username=username).exists():
            raise ValidationError(f"The username: {username} is already in use.")

        # Check if email is already in use.
        if Collaborator.objects.filter(email=email).exists():
            raise ValidationError(f"The email: {email} is already in use.")

        # Check if employee number is already in user
        if Collaborator.objects.filter(employee_number=employee_number).exists():
            raise ValidationError(f"The employee number: {employee_number} is already in use.")

        role, created = Role.objects.get_or_create(name=role_name)

        collaborator = Collaborator.objects.create(first_name=first_name,
                                                   last_name=last_name,
                                                   username=username,
                                                   email=email,
                                                   role=role,
                                                   employee_number=employee_number)
        collaborator.set_password(password)
        # TODO: Add the user to the corresponding group before saving it.
        collaborator.save()

    # =====================================
    # CLIENTS SECTION
    # =====================================
    def get_all_clients(self) -> QuerySet[Client]:
        try:
            return Client.objects.all()
        except Exception as e:
            print(f"Error retrieving clients: {e}")
            return Client.objects.none()

    # =====================================
    # CONTRACTS SECTION
    # =====================================
    def get_all_contracts(self) -> QuerySet[Contract]:
        try:
            return Contract.objects.all()
        except Exception as e:
            print(f"Error retrieving clients: {e}")
            return Contract.objects.none()

    # =====================================
    # EVENTS SECTION
    # =====================================
    def get_all_events(self) -> QuerySet[Event]:
        try:
            return Event.objects.all()
        except Exception as e:
            print(f"Error retrieving events: {e}")
            return Event.objects.none()

    def get_events_for_collaborator(self, collaborator_id: int) -> QuerySet[Event]:
        """
        Retrieves all events attributed to a specific collaborator.

        Args:
        collaborator_id (int): The ID of the collaborator.

        Returns:
        QuerySet[Event]: A queryset of events attributed to the collaborator.
        """
        try:
            return Event.objects.filter(support_contact_id=collaborator_id)
        except Exception as e:
            print(f"Error retrieving events for collaborator {collaborator_id}: {e}")
            return Event.objects.none()

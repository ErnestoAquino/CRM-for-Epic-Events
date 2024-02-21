from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db import DatabaseError
from django.db.models.query import QuerySet

from datetime import datetime

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
                              employee_number: str) -> Collaborator:

        # Check if the username is already in use.
        if Collaborator.objects.filter(username=username).exists():
            raise ValidationError(f"The username: {username} is already in use.")

        # Check if email is already in use.
        if Collaborator.objects.filter(email=email).exists():
            raise ValidationError(f"The email: {email} is already in use.")

        # Check if employee number is already in user
        if Collaborator.objects.filter(employee_number=employee_number).exists():
            raise ValidationError(f"The employee number: {employee_number} is already in use.")

        # Get or create the role
        role, created = Role.objects.get_or_create(name=role_name)

        # Create the Collaborator instance
        collaborator = Collaborator(first_name=first_name,
                                    last_name=last_name,
                                    username=username,
                                    email=email,
                                    role=role,
                                    employee_number=employee_number)

        collaborator.set_password(password)

        # Add the collaborator to the corresponding group.
        role_to_group = {
            'management': 'management_team',
            'sales': 'sales_team',
            'support': 'support_team',
        }
        group_name = role_to_group.get(role_name)
        if group_name:
            group, group_created = Group.objects.get_or_create(name = group_name)
            collaborator.save()
            collaborator.groups.add(group)
            collaborator.save()

        return collaborator

    @staticmethod
    def modify_collaborator(collaborator: Collaborator, modifications: dict) -> Collaborator:
        if 'username' in modifications and Collaborator.objects.exclude(id = collaborator.id).filter(
                username = modifications['username']).exists():
            raise ValidationError(
                f"The username: {modifications['username']} is already in use by another collaborator.")

        if 'email' in modifications and Collaborator.objects.exclude(id = collaborator.id).filter(
                email = modifications['email']).exists():
            raise ValidationError(f"The email: {modifications['email']} is already in use by another collaborator.")

        if 'employee_number' in modifications and Collaborator.objects.exclude(id = collaborator.id).filter(
                employee_number = modifications['employee_number']).exists():
            raise ValidationError(
                f"The employee number: {modifications['employee_number']} is already in use by another collaborator.")

        role_modified = False

        if 'role_name' in modifications:
            new_role_name = modifications.pop('role_name')
            if collaborator.role.name != new_role_name:
                role_modified = True
                role, created = Role.objects.get_or_create(name = new_role_name)
                collaborator.role = role

        for field, value in modifications.items():
            setattr(collaborator, field, value)

        try:
            if role_modified:
                collaborator.groups.clear()
                role_to_group = {
                    'management': 'management_team',
                    'sales': 'sales_team',
                    'support': 'support_team',
                }
                new_group_name = role_to_group.get(collaborator.role.name)
                if new_group_name:
                    new_group, _ = Group.objects.get_or_create(name = new_group_name)
                    collaborator.groups.add(new_group)

            collaborator.save()

        except ValidationError as e:
            raise ValidationError(f"Validation error: {e}") from e
        except DatabaseError as e:
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            raise Exception("Unexpected error updating collaborator.") from e

        return collaborator

    @staticmethod
    def get_all_non_superuser_collaborators() -> QuerySet[Collaborator]:
        """
        Retrieve all collaborators who are not superusers from the database.

        Returns:
            QuerySet: A queryset containing all non-superuser collaborators.
        """
        try:
            # Attempt to retrieve all collaborators who are not superusers
            return Collaborator.objects.exclude(is_superuser=True)
        except DatabaseError as e:
            # Raise a new exception if there's a problem accessing the database
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            # Raise a generic exception if an unexpected error occurs
            raise Exception("Unexpected error retrieving collaborators.") from e

    @staticmethod
    def delete_collaborator(collaborator: Collaborator) -> None:
        """
        Deletes a collaborator from the database.

        Args:
            collaborator (Collaborator): The collaborator to delete.

        Raises:
            DatabaseError: If there's a problem accessing the database.
            Exception: If an unexpected error occurs during deletion.
        """
        try:
            # Attempt to delete the collaborator
            collaborator.delete()
        except DatabaseError as e:
            # Raise a new exception if there's a problem accessing the database
            raise DatabaseError(f"Problem with database access") from e
        except Exception as e:
            # Raise a generic exception if an unexpected error occurs
            raise Exception("Unexpected error deleting collaborator") from e

    # ===================================== CLIENTS SECTION =====================================
    @staticmethod
    def create_client(full_name: str,
                      email: str,
                      phone: str,
                      company_name: str,
                      sales_contact: Collaborator):

        # Check if email is already in use.
        if Client.objects.filter(email=email).exists():
            raise ValidationError(f"The {email} is already in use.")

        # Create the new client
        client = Client(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            sales_contact=sales_contact
        )

        # Saves the new client to the database
        client.save()

        return client

    def get_clients_for_collaborator(self, collaborator_id: int) -> QuerySet[Event]:
        """
        Retrieves all clients attributed to a specific sales contact.

        Args:
        sales_contact_id (int): The ID of the sales contact.

        Returns:
        QuerySet[Client]: A queryset of clients attributed to the sales contact.
        """
        try:
            return Client.objects.filter(sales_contact_id=collaborator_id)
        except Exception as e:
            print(f"Error retrieving events for collaborator {collaborator_id}: {e}")
            return Client.objects.none()

    def get_all_clients(self) -> QuerySet[Client]:
        """
        Retrieve all clients from the database.

        Returns:
            QuerySet: A queryset containing all clients.
        """
        try:
            # Attempt to retrieve all clients from the database
            return Client.objects.all()
        except DatabaseError as e:
            # Raise a new exception if there's a problem accessing the database
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            # Raise a generic exception if an unexpected error occurs
            raise Exception("Unexpected error retrieving clients.") from e

    # ===================================== CONTRACTS SECTION =====================================
    @staticmethod
    def create_contract(client: Client, sales_contact: Collaborator, total_amount: float,
                        amount_remaining: float, status: str) -> Contract:
        """
        Creates a new contract and saves it to the database.

        This method creates a new contract object with the provided parameters,
        saves it to the database, and returns the created contract instance.

        Args:
            client (Client): The client associated with the contract.
            sales_contact (Collaborator): The sales contact associated with the contract.
            total_amount (float): The total amount of the contract.
            amount_remaining (float): The remaining amount to be paid on the contract.
            status (str): The status of the contract.

        Returns:
            Contract: The newly created contract object.

        Raises:
            ValidationError: If there's a validation error during saving.
            DatabaseError: If there's a problem accessing the database.
            Exception: If an unexpected error occurs during contract creation.
        """
        try:
            contract = Contract(
                client=client,
                sales_contact=sales_contact,
                total_amount=total_amount,
                amount_remaining=amount_remaining,
                status=status
            )
            # Save the contract to the database
            contract.save()
            return contract
        except ValidationError as e:
            # Handle validation error
            raise ValidationError(f"Validation error: {e}")
        except DatabaseError as e:
            # Handle database error
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            # Handle unexpected error
            raise Exception("Unequal error retrieving contracts.") from e

    @staticmethod
    def modify_contract(contract: Contract, modifications: dict) -> Contract:
        """
        Modifies an existing contract with the provided data.

        Args:
            contract (Contract): Instance of the contract to modify.
            modifications (dict): Dictionary with the fields to modify and their new values.

        Returns:
            Contract: The modified contract.

        Raises:
            ValidationError: If there's a validation error with the provided data.
            DatabaseError: If there's an issue accessing the database.
        """
        try:
            for key, value in modifications.items():
                setattr(contract, key, value)

            contract.full_clean()
            contract.save()
            return contract

        except ValidationError as e:
            raise ValidationError(f"Validation error while modifying the contract: {e}")
        except DatabaseError as e:
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            raise Exception("Unexpected error modifying contracts.") from e

    def get_filtered_contracts_for_collaborator(self, collaborator_id: int,
                                                filter_type: str = None) -> QuerySet[Contract]:
        try:
            # Create a new contract instance
            clients = self.get_clients_for_collaborator(collaborator_id)
            contracts = Contract.objects.filter(client__in=clients)

            if filter_type == "signed":
                contracts = contracts.filter(status="signed")

            elif filter_type == "not_signed":
                contracts = contracts.filter(status="not_signed")

            # Filters contracts with amount_remaining greater than (__gt) 0, indicating they are not fully paid yet.
            elif filter_type == "no_fully_paid":
                contracts = contracts.filter(amount_remaining__gt=0)

            return contracts
        except Exception as e:
            print(f"An unexpected error occurred while retrieving contracts for collaborator ID {collaborator_id}: {e}")
            return Contract.objects.none()

    def get_all_contracts(self) -> QuerySet[Contract]:
        """
        Retrieve all contracts from the database.

        Returns:
            QuerySet: A queryset containing all contracts.
        """
        try:
            # Attempt retrieve all clients from the database
            return Contract.objects.all()
        except DatabaseError as e:
            raise DatabaseError("Problem with the database") from e
        except Exception as e:
            raise Exception("Unexpected error occurred while retrieving contracts.") from e

    # ===================================== EVENTS SECTION =====================================
    @staticmethod
    def create_event(contract: Contract,
                     client_name: str,
                     name: str,
                     client_contact: str,
                     start_date: datetime,
                     end_date: datetime,
                     location: str,
                     attendees: int,
                     notes: str) -> Event:

        # Create the new event
        event = Event(
            contract = contract,
            client_name = client_name,
            name = name,
            client_contact = client_contact,
            start_date = start_date,
            end_date = end_date,
            location = location,
            attendees = attendees,
            notes = notes
        )
        # Saves the new event to the database
        event.save()

        return event

    def get_all_events(self) -> QuerySet[Event]:
        try:
            return Event.objects.all()
        except DatabaseError as e:
            print(f"Error: {e}")
            return Event.objects.none()
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

    def modify_event_by_id(self, event_id: int, **kwargs) -> Event | None:
        """
        Modifies an existing event with the provided data.

        Args:
            event_id (int): The ID of event to modify.
            **kwargs: Field arguments to update in the event.

        Returns:
            Event: The modified event if operation is successful; None otherwise

        """
        try:
            # Get event by ID
            event = Event.objects.get(id=event_id)

            # Update even fields with provided kwargs
            for field, value in kwargs.items():
                setattr(event, field, value)

            # Save changes to the database
            event.save()

            return event  # Returns the modified event.
        except Event.DoesNotExist:
            # TODO: Sentry
            print(f"No event found with id: {event_id}")
            return None
        except Exception as e:
            # TODO: Sentry
            print(f"Error modifying event {event_id}: {e}")
            return None

    def get_event_by_id(self, event_id: int) -> Event | None:
        """
        Retrieve an event by ID.

        Args:
            event_id (int): The ID of the event to retrieve.
        Returns:
            Event if found; None otherwise.
        """
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            print(f"No event found with id: {event_id}")
            return None
        except Exception as e:
            print(f"Error retrieving event {event_id}: {e}")
            return None

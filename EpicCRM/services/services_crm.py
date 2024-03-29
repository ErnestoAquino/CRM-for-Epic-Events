from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db import DatabaseError
from django.db.models.query import QuerySet
from typing import Optional
from sentry_sdk import capture_exception
from sentry_sdk import capture_message
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
        try:
            # Check if the username, email, or employee number is already in use.
            if Collaborator.objects.filter(username=username).exists():
                raise ValidationError(f"The username: {username} is already in use.")
            if Collaborator.objects.filter(email=email).exists():
                raise ValidationError(f"The email: {email} is already in use.")
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
            collaborator.full_clean()  # This will run model field validations
            collaborator.save()

            capture_message(f"Collaborator {username} has been registered.")

            # Add the collaborator to the corresponding group.
            role_to_group = {
                'management': 'management_team',
                'sales': 'sales_team',
                'support': 'support_team',
            }
            group_name = role_to_group.get(role_name)
            if group_name:
                group, group_created = Group.objects.get_or_create(name=group_name)
                collaborator.groups.add(group)
                collaborator.save()

            return collaborator
        except ValidationError as e:
            capture_exception(e)
            raise ValidationError(f"Validation error: {e}") from e
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("Unexpected error creating collaborator") from e

    @staticmethod
    def modify_collaborator(collaborator: Collaborator, modifications: dict) -> Collaborator:
        if 'username' in modifications and Collaborator.objects.exclude(id=collaborator.id).filter(
                username=modifications['username']).exists():
            raise ValidationError(
                f"The username: {modifications['username']} is already in use by another collaborator.")

        if 'email' in modifications and Collaborator.objects.exclude(id=collaborator.id).filter(
                email=modifications['email']).exists():
            raise ValidationError(f"The email: {modifications['email']} is already in use by another collaborator.")

        if 'employee_number' in modifications and Collaborator.objects.exclude(id=collaborator.id).filter(
                employee_number=modifications['employee_number']).exists():
            raise ValidationError(
                f"The employee number: {modifications['employee_number']} is already in use by another collaborator.")

        role_modified = False

        if 'role_name' in modifications:
            new_role_name = modifications.pop('role_name')
            if collaborator.role.name != new_role_name:
                role_modified = True
                role, created = Role.objects.get_or_create(name=new_role_name)
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
                    new_group, _ = Group.objects.get_or_create(name=new_group_name)
                    collaborator.groups.add(new_group)

            collaborator.save()
            capture_message(f"The Collaborator {collaborator.username} has been modified.")

        except ValidationError as e:
            capture_exception(e)
            raise ValidationError(f"Validation error: {e}") from e
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
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
            capture_exception(e)
            # Raise a new exception if there's a problem accessing the database
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            # Raise a generic exception if an unexpected error occurs
            raise Exception("Unexpected error retrieving collaborators.") from e

    @staticmethod
    def get_support_collaborators() -> QuerySet[Collaborator]:
        """
        Retrieve all collaborators with the 'support' role from the database.

        Returns:
            A QuerySet of Collaborator instances who have the 'support' role.
        Raises:
            DatabaseError: If there's a problem accessing the database.
            Exception: If an unexpected error occurs.
        """
        try:
            support_collaborators = Collaborator.objects.filter(role__name="support")
            return support_collaborators
        except DatabaseError as e:
            capture_exception(e)
            # Raise a new exception if there's a problem accessing the database
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
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
            capture_exception(e)
            # Raise a new exception if there's a problem accessing the database
            raise DatabaseError(f"Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            # Raise a generic exception if an unexpected error occurs
            raise Exception("Unexpected error deleting collaborator") from e

    # ===================================== CLIENTS SECTION =====================================
    @staticmethod
    def create_client(full_name: str,
                      email: str,
                      phone: str,
                      company_name: str,
                      sales_contact: Collaborator) -> Client:

        # Check if email is already in use.
        if Client.objects.filter(email=email).exists():
            raise ValidationError(f"The {email} is already in use.")

        try:
            # Create the new client
            new_client = Client(
                full_name=full_name,
                email=email,
                phone=phone,
                company_name=company_name,
                sales_contact=sales_contact
            )

            # Try to save the new client to the database
            new_client.full_clean()
            new_client.save()

            return new_client
        except ValidationError as e:
            capture_exception(e)
            raise ValidationError(f"Validation error: {e}") from e
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("Unexpected error creating client") from e

    @staticmethod
    def get_clients_for_collaborator(collaborator_id: int) -> QuerySet[Event]:
        """
        Retrieves clients associated with a specific collaborator from the database.

        Args:
            collaborator_id (int): The ID of the collaborator.

        Returns:
            QuerySet[Client]: Queryset of clients associated with the collaborator.

        Raises:
            DatabaseError: If there is a problem with database access.
            Exception: If an unexpected error occurs while retrieving clients.
        """
        try:
            clients_of_collaborator = Client.objects.filter(sales_contact_id=collaborator_id)
            return clients_of_collaborator
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("Unexpected error retrieving clients") from e

    @staticmethod
    def get_all_clients() -> QuerySet[Client]:
        """
        Retrieve all clients from the database.

        Returns:
            QuerySet: A queryset containing all clients.
        """
        try:
            # Attempt to retrieve all clients from the database
            return Client.objects.all()
        except DatabaseError as e:
            capture_exception(e)
            # Raise a new exception if there's a problem accessing the database
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            # Raise a generic exception if an unexpected error occurs
            raise Exception("Unexpected error retrieving clients.") from e

    @staticmethod
    def modify_client(client: Client, modifications: dict) -> Client:
        """
        Modifies an existing client with the provided data.

        Args:
            client (Client): Instance of the client to modify.
            modifications (dict): Dictionary with the fields to modify and their new values.

        Returns:
            Client: The modified client.

        Raises:
            ValidationError: If there's a validation error with the provided data.
            DatabaseError: If there's an issue accessing the database.
        """
        try:
            # Update client attributes with provided modifications.
            for key, value in modifications.items():
                setattr(client, key, value)

            client.full_clean()  # Perform full validation
            client.save()  # Save the modified client
            return client

        except ValidationError as e:
            capture_exception(e)
            raise ValidationError(f"Validation error while modifying the client: {e}") from e
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("Unexpected error modifying client.") from e

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

            if status == 'signed':
                capture_message(f"Contract signed with client {client.id} with sales contact {sales_contact.id}")

            return contract
        except ValidationError as e:
            capture_exception(e)
            # Handle validation error
            raise ValidationError(f"Validation error: {e}")
        except DatabaseError as e:
            capture_exception(e)
            # Handle database error
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
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
            capture_exception(e)
            raise ValidationError(f"Validation error while modifying the contract: {e}")
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("Unexpected error modifying contracts.") from e

    def get_filtered_contracts_for_collaborator(self, collaborator_id: int,
                                                filter_type: str = None) -> QuerySet[Contract]:
        """
        Retrieve filtered contracts associated with a specific collaborator.

        Args:
            collaborator_id (int): The ID of the collaborator whose contracts are to be retrieved.
            filter_type (str, optional): The type of filter to be applied to the contracts.
                Possible values are:
                    - "signed": Filters contracts that are signed.
                    - "not_signed": Filters contracts that are not signed.
                    - "no_fully_paid": Filters contracts that are not fully paid yet.
                    - None: No additional filtering.
                Defaults to None.

        Returns:
            QuerySet[Contract]: A queryset containing the filtered contracts associated with the collaborator.

        Raises:
            DatabaseError: If there is a problem with database access.
            ValueError: If the provided filter_type is unsupported.
            Exception: For unexpected errors during the retrieval process.
        """
        try:
            # Retrieve clients associated with the collaborator
            clients = self.get_clients_for_collaborator(collaborator_id)

            # Filter contracts based on clients.
            contracts = Contract.objects.filter(client__in=clients)

            # Apply additional filters based on filter_type
            match filter_type:
                case "signed":
                    contracts = contracts.filter(status="signed")
                case "not_signed":
                    contracts = contracts.filter(status="not_signed")
                case "no_fully_paid":
                    contracts = contracts.filter(amount_remaining__gt=0)
                case None:
                    pass  # No additional filtering if filter_type is None
                case _:
                    raise ValueError(f"Unsupported filter type: {filter_type}")

            return contracts
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("Unexpected error retrieving contracts.") from e

    @staticmethod
    def get_all_contracts() -> QuerySet[Contract]:
        """
        Retrieve all contracts from the database.

        Returns:
            QuerySet: A queryset containing all contracts.
        """
        try:
            # Attempt retrieve all clients from the database
            return Contract.objects.all()
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with the database") from e
        except Exception as e:
            capture_exception(e)
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
        """
        Creates a new event and saves it to the database.

        This method creates a new event object with the provided parameters,
        saves it to the database, and returns the created event instance.

        Args:
            contract (Contract): The contract associated with the event.
            client_name (str): The name of the client.
            name (str): The name of the event.
            client_contact (str): The contact information for the client.
            start_date (datetime): The start date and time of the event.
            end_date (datetime): The end date and time of the event.
            location (str): The location of the event.
            attendees (int): The number of attendees expected at the event.
            notes (str): Any additional notes related to the event.

        Returns:
            Event: The newly created event object.

        Raises:
            ValidationError: If there's a validation error during saving.
            DatabaseError: If there's a problem accessing the database.
            Exception: If an unexpected error occurs during event creation.
        """

        try:
            event = Event(
                contract=contract,
                client_name=client_name,
                name=name,
                client_contact=client_contact,
                start_date=start_date,
                end_date=end_date,
                location=location,
                attendees=attendees,
                notes=notes
            )
            # Saves the new event to the database
            event.save()
            return event
        except ValidationError as e:
            raise ValidationError(f"ValidationError: {e}") from e
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with the database") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("An unexpected error occurred while creating the event") from e

    @staticmethod
    def get_all_events_with_optional_filter(support_contact_required: Optional[bool] = None) -> QuerySet[Event]:
        """
        Retrieves all events from the database with an optional filter based on the presence or absence of
         a support contact.

        Args:
            support_contact_required(Optional[bool]):If True, return events with a support contact assigned.
                                                     If False, return events without a support contact assigned.
                                                     If None, returns all events without any filter applied.

        Returns:
            QuerySet[Event]: A queryset of Event objects filtered based on the support_contact_required parameter.

        Raises:
            DatabaseError: If an issue occurs accessing the database.
            Exception: For any unexpected error during the retrieval of events.
        """

        try:
            events = Event.objects.all()
            match support_contact_required:
                case None:
                    return events
                case True:
                    events = events.exclude(support_contact__isnull=True)
                    return events
                case False:
                    events = events.filter(support_contact__isnull=True)
                    return events
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with the database access during the retrieval of events.") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("Unexpected error occurred while retrieving events.") from e

    @staticmethod
    def add_support_contact_to_event(event: Event, support_contact: Collaborator) -> Event:
        """
        Assigns a support collaborator to an event and returns the modified event.

        Args:
            event (Event): The event to assign the support collaborator to.
            support_contact (Collaborator): The collaborator to be assigned as support.

        Returns:
            Event: The modified event with the new support contact assigned.

        Raises:
            DatabaseError: If there's a problem accessing the database.
            Exception: If an unexpected error occurs during the assignment.
        """
        try:
            # Assign the support collaborator to the event
            event.support_contact = support_contact

            # Validate changes
            event.full_clean()

            # Save the event with the new support contact
            event.save()
            return event

        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with the database access during the support contact assignment") from e
        except Exception as e:
            capture_exception(e)
            raise Exception("Unexpected error occurred during the support contact assignment") from e

    @staticmethod
    def get_all_events() -> QuerySet[Event]:
        try:
            return Event.objects.all()
        except DatabaseError as e:
            capture_exception(e)
            print(f"Error: {e}")
            return Event.objects.none()
        except Exception as e:
            capture_exception(e)
            print(f"Error retrieving events: {e}")
            return Event.objects.none()

    @staticmethod
    def get_events_for_collaborator(collaborator_id: int) -> QuerySet[Event]:
        """
        Retrieves all events attributed to a specific collaborator.

        Args:
        collaborator_id (int): The ID of the collaborator.

        Returns:
        QuerySet[Event]: A queryset of events attributed to the collaborator.
        """
        try:
            return Event.objects.filter(support_contact_id=collaborator_id)
        except DatabaseError as e:
            capture_exception(e)
            raise DatabaseError("Problem with the database access") from e
        except Exception as e:
            capture_exception(e)
            print(f"Error retrieving events for collaborator {collaborator_id}: {e}")

    @staticmethod
    def modify_event_by_id(event_id: int, **kwargs) -> Event | None:
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
        except Event.DoesNotExist as e:
            capture_exception(e)
            print(f"No event found with id: {event_id}")
            return None
        except Exception as e:
            capture_exception(e)
            print(f"Error modifying event {event_id}: {e}")
            return None

    @staticmethod
    def modify_event(event: Event, modifications: dict) -> Event:
        """
        Modifies an existing event with the provided data.

        Args:
            event (Event): Instance of the event to modify.
            modifications (dict): Dictionary with the fields to modify and their new values.

        Returns:
            Event: The modified event.

        Raises:
            ValidationError: If there's a validation error with the provided data.
            DatabaseError: If there's an issue accessing the database.
            Exception: If an unexpected error occurs during the modification.
        """
        try:
            # Apply modifications
            for key, value in modifications.items():
                setattr(event, key, value)

            # Validate the event instance before saving
            event.full_clean()
            # Save the modified event to the database
            event.save()
            return event

        except ValidationError as e:
            capture_exception(e)
            # Reraise validation errors with additional context
            raise ValidationError(f"Validation error while modifying the event: {e}")
        except DatabaseError as e:
            capture_exception(e)
            # Handle database access issues
            raise DatabaseError("Problem with database access while modifying the event.") from e
        except Exception as e:
            capture_exception(e)
            # Handle unexpected errors
            raise Exception(f"Unexpected error occurred while modifying the event: {e}")

    @staticmethod
    def get_event_by_id(event_id: int) -> Event | None:
        """
        Retrieve an event by ID.

        Args:
            event_id (int): The ID of the event to retrieve.
        Returns:
            Event if found; None otherwise.
        """
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist as e:
            capture_exception(e)
            print(f"No event found with id: {event_id}")
            return None
        except Exception as e:
            capture_exception(e)
            print(f"Error retrieving event {event_id}: {e}")
            return None

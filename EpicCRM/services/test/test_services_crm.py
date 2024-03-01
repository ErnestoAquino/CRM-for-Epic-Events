import pytest
from unittest.mock import patch
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.contrib.auth import authenticate

from crm.models import Collaborator, Role
from ..services_crm import ServicesCRM


@pytest.mark.django_db
def test_authenticate_collaborator_success():
    # Create a collaborator for the test
    Collaborator.objects.create_user('testcollaborator', 'collaborator@example.com', 'testpassword')

    # Attempt to authenticate with correct credentials
    user = ServicesCRM.authenticate_collaborator(username = 'testcollaborator', password = 'testpassword')

    assert user is not None
    assert user.username == 'testcollaborator'


@pytest.mark.django_db
def test_authenticate_collaborator_incorrect_credentials():
    # Create a collaborator for the test
    Collaborator.objects.create_user('testcollaborator', 'collaborator@example.com', 'testpassword')

    # Attempt to authenticate with incorrect credentials
    with pytest.raises(ValidationError) as excinfo:
        ServicesCRM.authenticate_collaborator(username = 'testcollaborator', password = 'wrong-password')

    assert "Incorrect username or password" in str(excinfo.value)


@pytest.mark.django_db
def test_register_collaborator_success():
    first_name = "John"
    last_name = "Doe"
    username = "johndoe"
    password = "password123"
    email = "john.doe@example.com"
    role_name = "management"
    employee_number = "123456"

    collaborator = ServicesCRM.register_collaborator(
        first_name = first_name,
        last_name = last_name,
        username = username,
        password = password,
        email = email,
        role_name = role_name,
        employee_number = employee_number
    )

    assert collaborator.username == username
    assert collaborator.email == email
    assert collaborator.employee_number == employee_number
    assert collaborator.role.name == role_name

    group_names = collaborator.groups.values_list('name', flat = True)
    assert role_name + "_team" in group_names


@pytest.mark.django_db
def test_register_collaborator_with_existing_username():
    # Create an existing collaborator
    existing_user = Collaborator.objects.create(
        username = "existinguser",
        email = "existing@example.com",
        password = "password123",
        first_name = "Existing",
        last_name = "User",
        employee_number = "654321"
    )

    # Try to register a new collaborator with the same username
    with pytest.raises(ValidationError) as excinfo:
        ServicesCRM.register_collaborator(
            first_name = "New",
            last_name = "User",
            username = "existinguser",  # same username
            password = "password123",
            email = "new@example.com",
            role_name = "sales",
            employee_number = "123457"
        )

    assert "The username: existinguser is already in use." in str(excinfo.value)


@pytest.mark.django_db
def test_register_collaborator_with_existing_email():
    # Create an existing collaborator
    existing_user = Collaborator.objects.create(
        username = "user1",
        email = "existing@example.com",  # Existing email
        password = "password123",
        first_name = "Existing",
        last_name = "User",
        employee_number = "654321"
    )

    # Try to register a new collaborator with the same email
    with pytest.raises(ValidationError) as excinfo:
        ServicesCRM.register_collaborator(
            first_name = "New",
            last_name = "User",
            username = "newuser",
            password = "password123",
            email = "existing@example.com",  # Attempting to use an existing email
            role_name = "sales",
            employee_number = "123457"
        )

    assert "The email: existing@example.com is already in use." in str(excinfo.value)


@pytest.mark.django_db
def test_register_collaborator_with_existing_employee_number():
    # Create an existing collaborator
    existing_user = Collaborator.objects.create(
        username = "user2",
        email = "user2@example.com",
        password = "password123",
        first_name = "Existing",
        last_name = "User",
        employee_number = "654321"  # Existing employee number
    )

    # Try to register a new collaborator with the same employee number
    with pytest.raises(ValidationError) as excinfo:
        ServicesCRM.register_collaborator(
            first_name = "New",
            last_name = "User",
            username = "newuser2",
            password = "password123",
            email = "new2@example.com",
            role_name = "marketing",
            employee_number = "654321"  # Attempting to use an existing employee number
        )

    assert "The employee number: 654321 is already in use." in str(excinfo.value)


@pytest.mark.django_db
def test_get_all_non_superuser_collaborators_success():
    # Create collaborators in the database, some superusers and others not
    Collaborator.objects.create_user(username = "user1", email = "user1@example.com",
                                     password = "password", is_superuser = True, employee_number = "001")
    Collaborator.objects.create_user(username = "user2", email = "user2@example.com",
                                     password = "password", is_superuser = False, employee_number = "002")
    Collaborator.objects.create_user(username = "user3", email = "user3@example.com",
                                     password = "password", is_superuser = False, employee_number = "003")

    #  Call the get_all_non_superuser_collaborators function
    non_superusers = ServicesCRM.get_all_non_superuser_collaborators()

    # Check that the returned QuerySet contains all collaborators who are not superusers and does not
    # include any superuser
    assert non_superusers.count() == 2  # There should be 2 collaborators who are not superusers
    for collaborator in non_superusers:
        assert not collaborator.is_superuser  # Ensure none is a superuser


@pytest.mark.django_db
def test_get_all_non_superuser_collaborators_with_no_collaborators():
    Collaborator.objects.all().delete()

    # Call the function to get all collaborators who are not superusers
    non_superuser_collaborators = ServicesCRM.get_all_non_superuser_collaborators()

    # Verify that the returned QuerySet is empty
    assert not non_superuser_collaborators.exists()


@pytest.mark.django_db
def test_get_all_non_superuser_collaborators_with_only_superusers():
    # Only collaborators marked as superusers in the database
    Collaborator.objects.create_user(username="superuser1", email="superuser1@example.com", password="password",
                                     is_superuser=True, employee_number="001")
    Collaborator.objects.create_user(username="superuser2", email="superuser2@example.com", password="password",
                                     is_superuser=True, employee_number="002")

    # Call the get_all_non_superuser_collaborators function
    non_superusers = ServicesCRM.get_all_non_superuser_collaborators()

    # Check that the returned QuerySet is empty
    assert not non_superusers.exists()


@pytest.mark.django_db
@patch('crm.models.Collaborator.objects.exclude')
def test_get_all_non_superuser_collaborators_database_error(mock_exclude):
    # Set up the mock to raise a DatabaseError when exclude() is called
    mock_exclude.side_effect = DatabaseError("Simulated database error")

    # Verify that a DatabaseError with the expected message is raised when calling the function
    with pytest.raises(DatabaseError) as excinfo:
        ServicesCRM.get_all_non_superuser_collaborators()
    assert "Problem with database access" in str(excinfo.value)


@pytest.mark.django_db
@patch('crm.models.Collaborator.objects.exclude')
def test_get_all_non_superuser_collaborators_unexpected_error(mock_exclude):
    # Set up the mock to raise a generic exception when exclude() is called
    mock_exclude.side_effect = Exception("Simulated unexpected error")

    # Verify that a generic exception with the expected message is raised when calling the function
    with pytest.raises(Exception) as excinfo:
        ServicesCRM.get_all_non_superuser_collaborators()
    assert "Unexpected error retrieving collaborators." in str(excinfo.value)



@pytest.mark.django_db
def test_modify_collaborator_success():
    # Create a Collaborator object and ensure there are no uniqueness conflicts with other collaborators
    original_username = 'original-user'
    new_username = 'newuser'
    original_email = 'original@example.com'
    new_email = 'new@example.com'
    original_employee_number = '123456'
    new_employee_number = '654321'
    role, _ = Role.objects.get_or_create(name='OrigRole')
    collaborator = Collaborator.objects.create(username=original_username, email=original_email,
                                               employee_number=original_employee_number, role=role)

    # Call modify_collaborator, passing the collaborator and a dictionary of valid modifications
    modifications = {
        'username': new_username,
        'email': new_email,
        'employee_number': new_employee_number,
        'role_name': 'NewRole'
    }
    updated_collaborator = ServicesCRM.modify_collaborator(collaborator, modifications)

    # Check that the collaborator's fields have been updated correctly in the database
    updated_collaborator.refresh_from_db()  # Refresh the collaborator instance from the DB to get the updated values
    assert updated_collaborator.username == new_username
    assert updated_collaborator.email == new_email
    assert updated_collaborator.employee_number == new_employee_number
    assert updated_collaborator.role.name == 'NewRole'


@pytest.mark.django_db
def test_modify_collaborator_with_existing_username():
    # Create two Collaborator objects
    role, _ = Role.objects.get_or_create(name='TestRole')
    collaborator1 = Collaborator.objects.create(username="user1", email="user1@example.com", employee_number="0001",
                                                role=role)
    Collaborator.objects.create(username="user2", email="user2@example.com", employee_number="0002", role=role)

    # Prepare modifications for one of them that include the username of the other
    modifications = {
        'username': 'user2',  # Trying to use an already existing username
    }

    # Try to update the collaborator with the already existing username
    with pytest.raises(ValidationError) as excinfo:
        ServicesCRM.modify_collaborator(collaborator1, modifications)

    #  ValidationError is raised indicating that the username is already in use
    assert "The username: user2 is already in use by another collaborator." in str(excinfo.value)


@pytest.mark.django_db
def test_modify_collaborator_with_existing_email():
    # Create two Collaborator objects
    role, _ = Role.objects.get_or_create(name='TestRole')
    collaborator1 = Collaborator.objects.create(username="uniqueuser1", email="uniqueemail1@example.com",
                                                employee_number="001", role=role)
    Collaborator.objects.create(username="uniqueuser2", email="commonemail@example.com", employee_number="002",
                                role=role)

    # Prepare modifications for one of them that include the email of the other
    modifications = {
        'email': 'commonemail@example.com',  # Attempting to use an existing email
    }

    # Attempt to update the collaborator with an existing email
    with pytest.raises(ValidationError) as excinfo:
        ServicesCRM.modify_collaborator(collaborator1, modifications)

    # A validationError is raised indicating the email is already in use
    assert "The email: commonemail@example.com is already in use by another collaborator." in str(excinfo.value)


@pytest.mark.django_db
def test_modify_collaborator_with_existing_employee_number():
    # Create two Collaborator objects
    role, _ = Role.objects.get_or_create(name='TestRole')
    collaborator1 = Collaborator.objects.create(username="uniqueuser1", email="uniqueemail1@example.com",
                                                employee_number="123", role=role)
    Collaborator.objects.create(username="uniqueuser2", email="uniqueemail2@example.com", employee_number="456",
                                role=role)

    # Prepare modifications for one of them that include the employee number of the other
    modifications = {
        'employee_number': '456',  # Attempting to use an existing employee number
    }

    # Attempt to update the collaborator with an existing employee number
    with pytest.raises(ValidationError) as excinfo:
        ServicesCRM.modify_collaborator(collaborator1, modifications)

    # Verification: Ensure that a ValidationError is raised indicating the employee number is already in use
    assert "The employee number: 456 is already in use by another collaborator." in str(excinfo.value)


@pytest.mark.django_db
def test_modify_collaborator_database_error():
    # Create a Collaborator object
    role, _ = Role.objects.get_or_create(name='TestRole')
    collaborator = Collaborator.objects.create(username="testuser", email="testemail@example.com",
                                               employee_number="789", role=role)

    # Prepare modifications that would normally be valid
    modifications = {
        'username': 'updateduser',
    }

    # Apply the mock only around the specific call being tested
    with patch('crm.models.Collaborator.save', side_effect=DatabaseError("Problem with database access")):
        # Try to update the collaborator, expecting a DatabaseError
        with pytest.raises(DatabaseError) as excinfo:
            ServicesCRM.modify_collaborator(collaborator, modifications)

    # Verify that a DatabaseError with the appropriate message is raised
    assert str(excinfo.value) == "Problem with database access"


from django.core.exceptions import ValidationError

from EpicCRM.crm.models import Collaborator
from EpicCRM.crm.models import Role


class ServicesCRM:

    def register_collaborator(self, first_name: str,
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
        collaborator.save()
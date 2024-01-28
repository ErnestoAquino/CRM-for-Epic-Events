from EpicCRM.crm.models import Collaborator
from EpicCRM.crm.models import Role


class ServicesCRM:
    def register_collaborator(self, username, password, email, role_name, employee_number):
        role, created = Role.objects.get_or_create(name=role_name)

        collaborator = Collaborator.objects.create(username=username,
                                                   email=email,
                                                   role=role,
                                                   employee_number=employee_number)
        collaborator.set_password(password)
        collaborator.save()

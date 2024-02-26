# Script to initialize groups, assign permissions, and create the first user in Django

import django
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password
from crm.models import Collaborator, Role

# Create groups
group_names = ['management_team', 'sales_team', 'support_team']
groups = {}
for group_name in group_names:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"Group '{group_name}' created successfully.")
    else:
        print(f"Group '{group_name}' already existed.")
    groups[group_name] = group

# Assign permissions to each group
permissions = {
    'management_team': ['view_client', 'manage_collaborators', 'manage_contracts_creation_modification',
                        'view_contract', 'view_event'],
    'sales_team': ['add_client', 'view_client', 'view_contract', 'view_event'],
    'support_team': ['view_client', 'view_contract', 'view_event'],
}

for group_name, perm_codenames in permissions.items():
    group = groups[group_name]
    for codename in perm_codenames:
        perm, created = Permission.objects.get_or_create(codename=codename)
        group.permissions.add(perm)
    print(f"Permissions successfully assigned to the group '{group_name}'.")

# Create the first user
role_name = "management"
role, created = Role.objects.get_or_create(name=role_name)
if created:
    print(f"Role '{role_name}' created successfully.")
else:
    print(f"The role '{role_name}' already existed.")

collaborator = Collaborator(
    first_name="Thomas",
    last_name="Girard",
    username="thomasg",
    email="thomas.girard@example.net",
    role=role,
    employee_number="9473",
    password=make_password("Manage123*")
)

collaborator.save()
groups['management_team'].user_set.add(collaborator)
print("Collaborator 'Thomas Girard' created and added to the 'management_team' group successfully.")

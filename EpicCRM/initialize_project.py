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


# Function to create a collaborator and add to a group
def create_collaborator(first_name, last_name, username, email, role_name, employee_number, password, group_name):
    role, created = Role.objects.get_or_create(name=role_name)
    if created:
        print(f"Role '{role_name}' created successfully.")
    else:
        print(f"The role '{role_name}' already existed.")

    collaborator = Collaborator(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        role=role,
        employee_number=employee_number,
        password=make_password(password)
    )

    collaborator.save()
    groups[group_name].user_set.add(collaborator)
    print(f"Collaborator '{first_name} {last_name}' created and added to the '{group_name}' group successfully.")


# Create users for each role and add them to respective groups
create_collaborator("Thomas", "Girard", "thomasg", "thomas.girard@example.net", "management", "9473", "Manage123*",
                    "management_team")
create_collaborator("Alex", "Johnson", "alexj", "alex.johnson@example.net", "sales", "9474", "Sales123*", "sales_team")
create_collaborator("Emma", "Smith", "emmas", "emma.smith@example.net", "support", "9475", "Support123*",
                    "support_team")

# CRM-for-Epic-Events

Epic Events is a company specializing in organizing a wide range of events, including parties, professional meetings, and off-site events for its clientele. To enhance its operational efficiency, Epic Events has embarked on developing a Customer Relationship Management (CRM) software. This software is pivotal in collecting and processing client data and event details, thereby streamlining communication across the company’s various departments, namely sales, support, and management.

The CRM software is crafted using Python 3.9 or newer versions and is designed as a command-line application, ensuring a focus on security measures such as SQL injection prevention, application of the principle of least privilege in data access, and efficient logging of exceptions and errors using Sentry. This project, being the twelfth project of the Python Application Developer path offered by OpenClassRooms, underscores the practical application of Django ORM for database management, demonstrating the integration of modern software development practices and tools in addressing real-world business needs.

## **Prerequisites**

- Python 3.9 or higher.
- PostgreSQL
- Sentry

Ensure PostgreSQL is installed and a superuser has been created.

## Getting Started

- Click
- Colorama
- Django ORM
- Sentry
- Python 3.9


## Deployment

First, clone the repository:
```bash
 git clone https://github.com/ErnestoAquino/CRM-for-Epic-Events.git
```

Navigate to the folder:
```bash
 cd CRM-for-Epic-Events/
```

Create a virtual enviroment:
```bash
 python3 -m venv env
```

Activate the virtual enviroment:
```bash
 source env/bin/activate
```

Install the requirements
```bash
 pip install -r requirements.txt
```


## **Database Configuration**

### **Step 1: Connect to PostgreSQL as Superuser**

First, connect to PostgreSQL using your superuser (typically **`postgres`**):

```bash
psql -U postgres
```

### **Step 2: Create a New User**

Create a new user and assign a password:

```sql
CREATE USER your_user WITH PASSWORD 'your_password';
```

### **Step 3: Create the Database**

As a superuser, create the database:

```sql
CREATE DATABASE your_db_name;
```

### **Step 4: Grant Permissions to the New User**

To enable **`your_user`** to execute Django migrations, they must have table creation permissions. Grant the necessary permissions:

```sql
\c your_db_name
```

```sql
-- Grant the privilege to connect to the database
GRANT CONNECT ON DATABASE your_db_name TO your_user;

-- Grant usage of the default schema and basic table privileges
GRANT USAGE ON SCHEMA public TO your_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;

-- Permission to create tables, necessary for applying Django migrations
GRANT CREATE ON SCHEMA public TO your_user;

-- Set default privileges for future tables created in the public schema
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO your_user;
```

## **Configure `secrets.json`**

Rename the file `secrets_example.json` to `secrets.json`:

```bash
mv secrets_example.json secrets.json
```

and add your passwords:

```json
{
  "DATABASE_PASSWORD": "your_password",
  "SENTRY_DSN": "your_sentry_dsn"
}
```

## **Connect the Database to Django**

In the `settings.py` file, replace the database name and user with your own:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_user',
        'PASSWORD': secrets['DATABASE_PASSWORD'],
        'HOST': 'localhost',
        'PORT': ''
    }
}
```

## **Apply Migrations**

```bash
 python EpicCRM/manage.py migrate
```

## **Configuration of Groups and Permissions**

From the Django shell:

```bash
python EpicCRM/manage.py shell
```

### **Create Groups [management_team, sales_team, support_team]**

```python
from django.contrib.auth.models import Group

# List of group names to be created
group_names = ['management_team', 'sales_team', 'support_team']

# Loop to create each group
for group_name in group_names:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"Group '{group_name}' created successfully.")
    else:
        print(f"Group '{group_name}' already existed.")
```

### **Assign Permissions to the management_team Group**

```python
from django.contrib.auth.models import Group, Permission

# Retrieve the group by its name
management_team = Group.objects.get(name='management_team')

# List of permission codenames to add to the group
perm_codenames = [
    'view_client',
    'manage_collaborators',
    'manage_contracts_creation_modification',
    'view_contract',
    'view_event',
]

# Retrieve permission objects based on codenames and add them to the group
for codename in perm_codenames:
    # Retrieve the permission by its codename
    perm = Permission.objects.get(codename=codename)
    # Add the permission to the group
    management_team.permissions.add(perm)

print("Permissions successfully added to the management_team group.")
```

### **Assign Permissions to the sales_team Group**

```python
from django.contrib.auth.models import Group, Permission

# Retrieve the group by its name
sales_team = Group.objects.get(name='sales_team')

# List of permission codenames to add to the group
perm_codenames = [
    'add_client',
    'view_client',
    'view_contract',
    'view_event',
]

# Retrieve permission objects based on codenames and add them to the group
for codename in perm_codenames:
    # Try to retrieve the permission by its codename
    try:
        perm = Permission.objects.get(codename=codename)
        # Add the permission to the group
        sales_team.permissions.add(perm)
    except Permission.DoesNotExist:
        print(f"The permission with codename '{codename}' does not exist.")

print("Permissions successfully added to the sales_team group.")
```

### **Assign Permissions to the support_team Group**

 Permissions to the support_team Group**

```python
from django.contrib.auth.models import Group, Permission

# Retrieve the group by its name
support_team = Group.objects.get(name='support_team')

# List of permission codenames to add to the group
perm_codenames = [
    'view_client',
    'view_contract',
    'view_event',
]

# Retrieve permission objects based on codenames and add them to the group
for codename in perm_codenames:
    # Try to retrieve the permission by its codename
    try:
        perm = Permission.objects.get(codename=codename)
        # Add the permission to the group
        support_team.permissions.add(perm)
    except Permission.DoesNotExist:
        print(f"The permission with codename '{codename}' does not exist.")

print("Permissions successfully added to the support_team group.")
```

### **Create the First User**

```python
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from crm.models import Collaborator, Role  

# Create the 'management' role
role_name = "management"
role, created = Role.objects.get_or_create(name=role_name)
if created:
    print(f"Role '{role_name}' created successfully.")
else:
    print(f"Role '{role_name}' already existed.")

# Create the new collaborator with the assigned role
collaborator = Collaborator(
    first_name="Thomas",
    last_name="Girard",
    username="thomasg",
    email="thomas.girard@example.net",
    role=role,
    employee_number="9473"
)

# Set the password
collaborator.set_password("Manage123*")

# Save the collaborator in the database
collaborator.save()

# Retrieve or create the 'management_team' group
group, created = Group.objects.get_or_create(name='management_team')
if created:
    print("Group 'management_team' created successfully.")
else:
    print("Group 'management_team' already existed.")

# Add the collaborator to the group
group.user_set.add(collaborator)

print("Collaborator successfully added to the 'management_team' group.")
```

Once your first collaborator is created, you can access the system using:

```bash
python EpicCRM/main.py
```

Connect using the collaborator's username and password you just created. Since the collaborator belongs to the management group, they can create other collaborators and assign roles. Create a collaborator with the sales role and another with the support role. The system checks the user's role to determine the main menu to be displayed. Sentry captures exceptions that may occur in the service layer, which communicates with the database. It also captures messages when a user tries to access a part of the system without the necessary permissions.

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

 Grant the privilege to connect to the database:
```sql
GRANT CONNECT ON DATABASE your_db_name TO your_user;
```

Grant usage of the default schema and basic table privileges:
```sql
GRANT USAGE ON SCHEMA public TO your_user;
```
```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_user;
```

Permission to create tables, necessary for applying Django migrations:
```sql
GRANT CREATE ON SCHEMA public TO your_user;
```

Set default privileges for future tables created in the public schema
```sql
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

## Project Setup


### Initial Setup with Script

To initialize the project with necessary groups, permissions, and a default management user, run the provided script using the following command:

```bash
python EpicCRM/manage.py shell < EpicCRM/initialize_project.py
```

This script automates the creation of essential groups (`management_team`, `sales_team`, `support_team`), assigns relevant permissions to each group, and creates a default user with management privileges.

### Starting the Application

After the initial setup, you can start the application by executing:

```bash
python EpicCRM/main.py
```

This command launches the application's command-line interface, allowing you to interact with the CRM functionalities.

### Logging In

To log in to the system, use the following credentials created during the initialization process:

- **Username:** `thomasg`
- **Password:** `Manage123*`

These credentials grant access to management functionalities, enabling full exploration and management of the CRM system.

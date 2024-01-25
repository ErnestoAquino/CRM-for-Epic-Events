from django.db.models import Model
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import DecimalField
from django.db.models import TextField
from django.db.models import IntegerField

from django.db.models import SET_NULL
from django.db.models import CASCADE
from django.contrib.auth.models import AbstractUser

from django.conf import settings


# Create your models here.
class Client(Model):
    """
    Represents a client in the CRM system.
    Stores the client's personal and company details.
    """
    full_name = CharField(max_length=100)  # The client's full name
    email = EmailField()  # The client's email address
    phone = CharField(max_length=20)  # The client's phone number
    company_name = CharField(max_length=100)  # Name of the client's company
    creation_date = DateTimeField(auto_now_add=True)  # Date when the client was added to the system
    last_updated = DateTimeField(auto_now=True)  # Date when the client's details were last updated
    sales_contact = ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=SET_NULL,
                               null=True)  # Sales contact for the client


class Contract(Model):
    """
    Represents a contract in the CRM system.
    Links a contract to a client and a sales contact.
    """
    CONTRACT_STATUS_CHOICES = [
        ('signed', 'Signed'),
        ('not_signed', 'Not Signed')
    ]
    client = ForeignKey(Client, on_delete=CASCADE)  # The client associated with the contract
    sales_contact = ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=SET_NULL,
                               null=True)   # Sales contact responsible for the contract
    total_amount = DecimalField(max_digits=10, decimal_places=2)
    amount_remaining = DecimalField(max_digits=10, decimal_places=2)
    creation_date = DateTimeField(auto_now_add=True)  # Date when the contract was created
    status = CharField(max_length=25,
                       choices=CONTRACT_STATUS_CHOICES,
                       default='not_signed')  # Current status of the contract


class Event(Model):
    """
    Represents an event in the CRM system.
    Links an event to a contract and stores event details.
    """
    contract = ForeignKey(Contract, on_delete=CASCADE)  # The contract associated with the event
    client_name = CharField(max_length=100)  # Name of the client associated with the event
    client_contact = TextField(blank=True, null=True)   # Contact details for the client related to the event
    start_date = DateTimeField()  # Start date and time of the event
    end_date = DateTimeField()  # End date and time of the event
    support_contact = ForeignKey(settings.AUTH_USER_MODEL,
                                 on_delete=SET_NULL,
                                 null=True)   # Support contact assigned to the event
    location = CharField(max_length=300)
    attendees = IntegerField()  # Number of attendees expected at the event
    notes = TextField(blank=True, null=True)  # Additional notes about the event


class Collaborator(AbstractUser):
    """
    Represents a collaborator (user) in the CRM system.
    Extends the default user model to include role information.
    """

    ROLE_CHOICES = [
        ('management', 'Management'),
        ('sales', 'Sales'),
        ('support', 'Support')
    ]

    role = CharField(max_length=10, choices=ROLE_CHOICES)

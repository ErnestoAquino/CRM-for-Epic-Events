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
    full_name = CharField(max_length=100)
    email = EmailField()
    phone = CharField(max_length=20)
    company_name = CharField(max_length=100)
    creation_date = DateTimeField(auto_now_add=True)
    last_updated = DateTimeField(auto_now=True)
    sales_contact = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)


class Contract(Model):
    CONTRACT_STATUS_CHOICES = [
        ('signed', 'Signed'),
        ('not_signed', 'Not Signed')
    ]
    client = ForeignKey(Client, on_delete=CASCADE)
    sales_contact = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    total_amount = DecimalField(max_digits=10, decimal_places=2)
    received_amount = DecimalField(max_digits=10, decimal_places=2)
    creation_date = DateTimeField(auto_now_add=True)
    status = CharField(max_length=25, choices=CONTRACT_STATUS_CHOICES, default='not_signed')


class Event(Model):
    contract = ForeignKey(Contract, on_delete=CASCADE)
    client = ForeignKey(Client, on_delete=CASCADE)
    client_contact = TextField(blank=True, null=True)
    start_date = DateTimeField()
    end_date = DateTimeField()
    support_contact = ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL, null=True)
    location = CharField(max_length=300)
    attendees = IntegerField()
    notes = TextField(blank=True, null=True)


class Collaborator(AbstractUser):
    ROLE_CHOICES = [
        ('management', 'Management'),
        ('sales', 'Sales'),
        ('support', 'Support')
    ]

    role = CharField(max_length=10, choices=ROLE_CHOICES)

# Generated by Django 5.0.1 on 2024-02-16 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0006_event_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="client_contact",
            field=models.TextField(default="N/A"),
            preserve_default=False,
        ),
    ]

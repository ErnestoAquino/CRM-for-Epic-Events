# Generated by Django 5.0.1 on 2024-01-26 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0002_collaborator_employee_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collaborator",
            name="employee_number",
            field=models.CharField(default=0, max_length=50, unique=True),
            preserve_default=False,
        ),
    ]

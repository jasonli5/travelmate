# Generated by Django 5.1.6 on 2025-04-14 18:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trips", "0003_inputtrip_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inputtrip",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

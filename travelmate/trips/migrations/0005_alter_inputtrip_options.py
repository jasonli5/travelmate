# Generated by Django 5.1.6 on 2025-04-14 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("trips", "0004_alter_inputtrip_created_at"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="inputtrip",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Trip",
                "verbose_name_plural": "Trips",
            },
        ),
    ]

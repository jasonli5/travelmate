# Generated by Django 5.2 on 2025-04-19 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trips", "0011_remove_inputtrip_activities"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="inputtrip",
            name="activities_list",
        ),
        migrations.AlterField(
            model_name="inputtrip",
            name="considerations",
            field=models.JSONField(
                blank=True, null=True, verbose_name="Additional Considerations"
            ),
        ),
    ]

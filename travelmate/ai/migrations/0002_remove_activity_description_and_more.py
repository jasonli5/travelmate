# Generated by Django 5.2 on 2025-04-19 00:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="activity",
            name="description",
        ),
        migrations.RemoveField(
            model_name="activity",
            name="is_ai_suggested",
        ),
    ]

# Generated by Django 4.2.10 on 2024-06-13 05:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_history'),
    ]

    operations = [
        migrations.RenameField(
            model_name='history',
            old_name='date',
            new_name='date_changed',
        ),
    ]

# Generated by Django 4.2 on 2023-04-15 22:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_muber_of_seats_aircraft_nuber_of_seats'),
    ]

    operations = [
        migrations.RenameField(
            model_name='aircraft',
            old_name='nuber_of_seats',
            new_name='number_of_seats',
        ),
    ]

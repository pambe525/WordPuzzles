# Generated by Django 4.2.2 on 2023-07-08 12:53

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('puzzles', '0012_rename_solvesession_solversession'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='solvedclue',
            unique_together={('clue', 'solver')},
        ),
    ]

# Generated by Django 4.0.3 on 2022-03-23 19:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('puzzles', '0003_session_elapsed_seconds_session_is_complete_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='reveal_clue_nums',
            new_name='revealed_clue_nums',
        ),
    ]

# Generated by Django 4.2.2 on 2023-06-30 19:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('puzzles', '0009_alter_groupsession_open_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupsession',
            name='open_at',
        ),
        migrations.AlterField(
            model_name='groupsession',
            name='start_at',
            field=models.DateTimeField(),
        ),
    ]

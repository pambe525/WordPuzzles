# Generated by Django 4.2.2 on 2023-07-08 17:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('puzzles', '0013_alter_solvedclue_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='solversession',
            name='revealed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='solversession',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='solversession',
            name='solved',
            field=models.IntegerField(default=0),
        ),
    ]

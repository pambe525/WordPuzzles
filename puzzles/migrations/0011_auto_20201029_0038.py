# Generated by Django 3.1.2 on 2020-10-29 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0010_auto_20201029_0022'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='is_ready',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='puzzle',
            name='shared_at',
            field=models.DateTimeField(null=True),
        ),
    ]

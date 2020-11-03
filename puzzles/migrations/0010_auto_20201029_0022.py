# Generated by Django 3.1.2 on 2020-10-29 00:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0009_puzzle'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='puzzle',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
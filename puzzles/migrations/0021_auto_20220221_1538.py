# Generated by Django 3.1 on 2022-02-21 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0020_auto_20220219_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wordpuzzle',
            name='desc',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='wordpuzzle',
            name='title',
            field=models.CharField(max_length=52, null=True),
        ),
    ]

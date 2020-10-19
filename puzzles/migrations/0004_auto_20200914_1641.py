# Generated by Django 3.1 on 2020-09-14 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0003_auto_20200914_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crossword',
            name='size',
            field=models.IntegerField(choices=[(11, '11 x 11'), (13, '13 x 13'), (15, '15 x 15')], default=13),
        ),
    ]
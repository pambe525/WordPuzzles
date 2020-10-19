# Generated by Django 3.1 on 2020-09-29 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzles', '0004_auto_20200914_1641'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crossword',
            name='blocks',
        ),
        migrations.AddField(
            model_name='crossword',
            name='grid_content',
            field=models.TextField(default='', max_length=625),
        ),
        migrations.AlterField(
            model_name='crossword',
            name='size',
            field=models.IntegerField(default=15),
        ),
    ]
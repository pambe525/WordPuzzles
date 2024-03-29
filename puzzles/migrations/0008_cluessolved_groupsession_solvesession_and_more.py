# Generated by Django 4.2.2 on 2023-06-30 19:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('puzzles', '0007_puzzlesession_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='CluesSolved',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solved', models.BooleanField(default=True)),
                ('clue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='puzzles.clue')),
            ],
        ),
        migrations.CreateModel(
            name='GroupSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('open_at', models.DateTimeField(null=True)),
                ('start_at', models.DateTimeField(null=True)),
                ('finish_at', models.DateTimeField(null=True)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('puzzle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='puzzles.wordpuzzle')),
            ],
        ),
        migrations.CreateModel(
            name='SolveSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(null=True)),
                ('group_session',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='puzzles.groupsession')),
                ('puzzle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='puzzles.wordpuzzle')),
                ('solver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='PuzzleSession',
        ),
        migrations.AddField(
            model_name='cluessolved',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='puzzles.solvesession'),
        ),
        migrations.AddField(
            model_name='cluessolved',
            name='solver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

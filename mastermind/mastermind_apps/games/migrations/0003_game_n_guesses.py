# Generated by Django 2.2 on 2020-01-20 17:56

from django.db import migrations, models


def forward(apps, schema_editor):
    game = apps.get_model('games', 'Game')
    db_alias = schema_editor.connection.alias
    games = game.objects.using(db_alias).all()

    for game in games:
        game.n_guesses = game.codes.using(db_alias).filter(
            game=game, is_guess=True).count()
        game.save()


def reverse(apps, schema_editor):
    game = apps.get_model('games', 'Game')
    db_alias = schema_editor.connection.alias
    games = game.objects.using(db_alias).all()

    for game in games:
        game.n_guesses = 0
        game.save()


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_auto_20200119_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='n_guesses',
            field=models.IntegerField(default=0),
        ),
        migrations.RunPython(code=forward, reverse_code=reverse)
    ]
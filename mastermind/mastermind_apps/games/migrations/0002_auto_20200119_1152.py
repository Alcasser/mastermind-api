# Generated by Django 2.2 on 2020-01-19 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='code',
            name='is_guess',
            field=models.BooleanField(default=True),
        ),
    ]
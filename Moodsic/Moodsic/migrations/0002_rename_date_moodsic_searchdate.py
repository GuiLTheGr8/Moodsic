# Generated by Django 4.2.3 on 2023-09-11 21:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Moodsic', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='moodsic',
            old_name='date',
            new_name='searchDate',
        ),
    ]

# Generated by Django 3.1 on 2020-09-05 10:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20200905_1033'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='winner',
            new_name='wineer',
        ),
    ]

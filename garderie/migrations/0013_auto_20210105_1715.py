# Generated by Django 3.1.3 on 2021-01-05 17:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('garderie', '0012_auto_20201221_1645'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reliableperson',
            old_name='parents',
            new_name='parent',
        ),
    ]
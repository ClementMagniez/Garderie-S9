# Generated by Django 3.1.3 on 2020-12-19 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('garderie', '0010_auto_20201219_1918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='date_end',
            field=models.DateTimeField(verbose_name='Date de fin'),
        ),
        migrations.AlterField(
            model_name='hourlyrate',
            name='date_end',
            field=models.DateTimeField(null=True, verbose_name='Date de fin'),
        ),
    ]
# Generated by Django 3.1.3 on 2021-01-27 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('garderie', '0003_auto_20210127_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='second_parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='second_parent', to='garderie.parent'),
        ),
        migrations.AlterField(
            model_name='child',
            name='first_name',
            field=models.CharField(max_length=100, verbose_name='Prénom'),
        ),
        migrations.AlterField(
            model_name='child',
            name='last_name',
            field=models.CharField(max_length=100, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='child',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='parent', to='garderie.parent'),
        ),
        migrations.AlterField(
            model_name='reliableperson',
            name='child',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='garderie.child', verbose_name='Enfant concerné'),
        ),
    ]
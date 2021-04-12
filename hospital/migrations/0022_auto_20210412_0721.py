# Generated by Django 3.0.5 on 2021-04-12 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0021_auto_20210412_0602'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='admitDate',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='age',
            field=models.PositiveSmallIntegerField(default=18),
        ),
        migrations.AlterField(
            model_name='patient',
            name='sex',
            field=models.CharField(default='-', max_length=1),
        ),
    ]

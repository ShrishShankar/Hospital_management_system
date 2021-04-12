# Generated by Django 3.0.5 on 2021-04-12 06:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0020_auto_20210411_1728'),
    ]

    operations = [
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('med_id', models.PositiveSmallIntegerField(primary_key=True, serialize=False)),
                ('med_name', models.CharField(max_length=100)),
                ('cost_for_one', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='patient',
            name='admitDate',
        ),
        migrations.AddField(
            model_name='appointment',
            name='appointmentTime',
            field=models.TimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='doctor',
            name='appointment_duration',
            field=models.PositiveSmallIntegerField(default=30),
        ),
        migrations.AddField(
            model_name='doctor',
            name='end_time',
            field=models.TimeField(default=datetime.time(17, 0)),
        ),
        migrations.AddField(
            model_name='doctor',
            name='fee',
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AddField(
            model_name='doctor',
            name='start_time',
            field=models.TimeField(default=datetime.time(9, 0)),
        ),
        migrations.AddField(
            model_name='patient',
            name='sex',
            field=models.CharField(default='M', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patientdischargedetails',
            name='doctorId',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='patientdischargedetails',
            name='doctorName',
            field=models.CharField(max_length=40, null=True),
        ),
    ]

# Generated by Django 3.1.7 on 2021-04-11 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0019_patient_bloodgroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patient',
            name='assignedDoctorId',
        ),
        migrations.AddField(
            model_name='patient',
            name='age',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='email',
            field=models.EmailField(default='example@email.com', max_length=256),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='sex',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='patient',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]

# Generated by Django 3.1.5 on 2021-01-28 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rm', '0025_auto_20210127_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawdata',
            name='interface_call',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rm.interfacecall'),
        ),
    ]

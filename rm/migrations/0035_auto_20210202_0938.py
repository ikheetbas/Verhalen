# Generated by Django 3.1.5 on 2021-02-02 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rm', '0034_auto_20210131_1719'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='interfacedefinition',
            unique_together={('system', 'data_set_type', 'interface_type')},
        ),
    ]

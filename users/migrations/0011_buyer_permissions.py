# Generated by Django 3.1.5 on 2021-02-08 08:25
import os
from typing import List

from django.db import migrations

def add_contract_permissions_to_buyer(apps, schema_editor):
    """
    Permissions names and codename for upload and api contract have changed.

    Here we add the new ones:
        * "Contracten upload"
        * "Contracten API"
    to the Buyer group
    """

    Group = apps.get_model('auth.Group')
    Permission = apps.get_model('auth.Permission')
    ContentType = apps.get_model("contenttypes", "ContentType")
    InterfaceCall = apps.get_model("rm", "InterfaceCall")

    content_type_interfaceCall = ContentType.objects.get_for_model(InterfaceCall)

    permission_upload_contract_file = dict(codename="contracten_upload",
                                           name="Contracten upload",
                                           content_type=content_type_interfaceCall)
    permission_call_contract_interface = dict(codename="contracten_api",
                                              name="Contracten API",
                                              content_type=content_type_interfaceCall)

    create_group_with_permissions(Group, Permission, "Buyer", [permission_upload_contract_file,
                                                               permission_call_contract_interface])


def create_group_with_permissions(Group, Permission, group_name, permissions: List[dict]):
    new_group, created = Group.objects.get_or_create(name=group_name)

    for permission in permissions:
        perm, created = Permission.objects.get_or_create(codename=permission['codename'],
                                                         defaults=dict(name=permission['name'],
                                                                       content_type=permission['content_type']))
        if created:
            print(
                f"  - {os.path.basename(__file__)}: created permission: {permission['codename']}, "
                f"adding it to {group_name}")
        else:
            print(
                f"  - {os.path.basename(__file__)}: found permission: {permission['codename']}, "
                f"adding it to {group_name}")
        new_group.permissions.add(perm)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0010_auto_20210127_1027'),
    ]

    operations = [
        migrations.RunPython(add_contract_permissions_to_buyer),
    ]

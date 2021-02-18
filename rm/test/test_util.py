from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models.functions import Now

from rm.constants import CONTRACTEN
from rm.models import System, DataSetType, InterfaceDefinition, DataPerOrgUnit, InterfaceCall
from stage.models import StageContract
from users.models import OrganizationalUnit



def login_user(client, user):
        client.logout()
        client.force_login(user)

def set_up_user_login_with_interface_call_and_contract(self,
                                                       superuser=True,
                                                       group_name=None,
                                                       username="John",
                                                       name_in_negometrix="John"):
    set_up_user_and_login(self,
                          superuser,
                          group_name,
                          username,
                          name_in_negometrix)
    set_up_static_data(self)
    set_up_process_contract_data(self)

def set_up_user_and_login(self,
                          superuser=False,
                          group_name=None,
                          username="John",
                          name_in_negometrix="John"):
    """
    When called without parameters, you get a superuser
    """
    if superuser:
        self.user = create_superuser()
    else:
        self.user = create_user(group_name=group_name,
                                username=username,
                                name_in_negometrix=name_in_negometrix,
                                )
    self.client.force_login(self.user)


def create_superuser(username="john", password="doe", **kwargs):

    user = get_user_model().objects.create(username=username,
                                           is_superuser=True,
                                           is_active=True,
                                           **kwargs
                                           )
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()
    user.save()
    return user


def create_user(username="john",
                password="doe",
                group_name=None,
                name_in_negometrix="J. Doe",
                **kwargs)-> get_user_model():
    user = get_user_model().objects.create(username=username,
                                           is_active=True,
                                           **kwargs
                                           )

    user.name_in_negometrix = name_in_negometrix
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()

    if group_name:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            message = f"Group {group_name} can not be found"
            raise Exception(message)
        user.groups.add(group)

    user.save()

    return user


def set_up_static_data(self):
    # Set up static data
    self.system_a = System.objects.create(name="SYSTEM_A")
    self.system = System.objects.get(name="Negometrix")
    self.data_set_type = DataSetType.objects.get_or_create(name=CONTRACTEN)
    self.interface_definition = InterfaceDefinition.objects.get(name="Contracten upload")
    self.org_unit = OrganizationalUnit.objects.create(name="MyTeam",
                                                      type=OrganizationalUnit.TEAM)
    self.user.org_units.add(self.org_unit)

def set_up_process_contract_data(self):
    self.interface_call_1 = InterfaceCall.objects.create(date_time_creation=Now(),
                                                         status='OK',
                                                         filename='Text.xls',
                                                         interface_definition=self.interface_definition,
                                                         user=self.user,
                                                         username=self.user.username,
                                                         user_email=self.user.email)

    self.data_per_org_unit = DataPerOrgUnit.objects.create(interface_call=self.interface_call_1,
                                                           org_unit=self.org_unit)

    self.stage_contract_1 = StageContract.objects.create(contract_nr='NL-123',
                                                         seq_nr=0,
                                                         description='Test Contract 1',
                                                         contract_owner='T. Ester',
                                                         contract_name='Test contract naam',
                                                         data_per_org_unit=self.data_per_org_unit)


def print_permissions_and_groups():
    all_permissions = Permission.objects.all()
    print("--------------------------------------")
    print("           PERMISSIONS")
    print("--------------------------------------")
    for permission in all_permissions:
        print(f"Found permission: {permission.codename}")
    print("--------------------------------------")

    all_groups = Group.objects.all()
    print("--------------------------------------")
    print("           GROUPS")
    print("--------------------------------------")
    for group in all_groups:
        print(f"Found group: {group.name}")
        permissions = group.permissions.all()
        if len(permissions) == 0:
            print("- has no permissions")
        for permission in permissions:
            print(f"- has permission: {permission.codename}")
    print("--------------------------------------")


def add_data_per_org_unit(interface_call, org_unit, active) -> DataPerOrgUnit:
    return DataPerOrgUnit.objects.create(interface_call=interface_call,
                                  active=active,
                                  org_unit=org_unit)


def create_interface_call(active, interface_definition) -> InterfaceCall:
    interface_call = InterfaceCall.objects.create(interface_definition=interface_definition,
                                                  status=InterfaceCall.ACTIVE if active else
                                                         InterfaceCall.READY_LOADING)
    return interface_call
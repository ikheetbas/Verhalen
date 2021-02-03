from django.db.models.functions import Now
from django.test import TestCase

from rm.models import System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from stage.models import StageContract


from users.models import CustomUser, OrganizationalUnit
from ..constants import CONTRACTEN, NEGOMETRIX

def setUpTeams(self):
    self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
    self.org_unit_EUS = OrganizationalUnit.objects.create(name="EUS", type=OrganizationalUnit.TEAM)
    self.org_unit_SITES = OrganizationalUnit.objects.create(name="SITES", type=OrganizationalUnit.TEAM)


def setUpNegometrixStaticData(self):
    self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
    self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
    self.interface_definition = InterfaceDefinition.objects.create(system=self.system,
                                                                   data_set_type=self.data_set_type,
                                                                   interface_type=InterfaceDefinition.UPLOAD)


def setUpNegometrixInterfaceCall_1_Active_IAAS_en_EUS(self):
    self.interface_call_1 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.ACTIVE)

    self.data_per_org_unit_IAAS_1 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_1,
                                                                  org_unit=self.org_unit_IAAS,
                                                                  active=True)
    self.contract_1_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_IAAS_1, seq_nr=0)
    self.contract_1_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_IAAS_1, seq_nr=1)

    self.data_per_org_unit_EUS_1 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_1,
                                                                 org_unit=self.org_unit_EUS,
                                                                 active=True)
    self.contract_1_3 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_1, seq_nr=2)
    self.contract_1_4 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_1, seq_nr=3)


def setUpNegometrixInterfaceCall_2_InActive_IAAS_en_EUS(self):
    self.interface_call_2 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.INACTIVE)
    self.data_per_org_unit_IAAS_2 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_2,
                                                                  org_unit=self.org_unit_IAAS,
                                                                  active=False)
    self.contract_2_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_IAAS_2, seq_nr=0)
    self.contract_2_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_IAAS_2, seq_nr=1)

    self.data_per_org_unit_EUS_2 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_2,
                                                                 org_unit=self.org_unit_EUS,
                                                                 active=False)
    self.contract_2_3 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_2, seq_nr=2)
    self.contract_2_4 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_2, seq_nr=3)


def setUpNegometrixInterfaceCall_3_InActive_IAAS_en_SITES(self):
    self.interface_call_3 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.INACTIVE)
    self.data_per_org_unit_IAAS_3 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_3,
                                                                  org_unit=self.org_unit_IAAS,
                                                                  active=False)
    self.contract_3_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_IAAS_3, seq_nr=0)
    self.contract_3_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_IAAS_3, seq_nr=1)

    self.data_per_org_unit_SITES_3 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_3,
                                                                   org_unit=self.org_unit_SITES,
                                                                   active=False)
    self.contract_3_3 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_SITES_3, seq_nr=2)
    self.contract_3_4 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_SITES_3, seq_nr=3)


def setUpNegometrixInterfaceCall_4_InActive_EUS_en_SITES(self):
    self.interface_call_4 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.INACTIVE)
    self.data_per_org_unit_EUS_4 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_4,
                                                                 org_unit=self.org_unit_EUS,
                                                                 active=False)
    self.contract_4_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_4, seq_nr=0)
    self.contract_4_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_4, seq_nr=1)

    self.data_per_org_unit_SITES_4 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_4,
                                                                   org_unit=self.org_unit_SITES,
                                                                   active=False)
    self.contract_4_3 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_SITES_4, seq_nr=2)
    self.contract_4_4 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_SITES_4, seq_nr=3)


def setUpNegometrixInterfaceCall_5_InActive_EUS(self):
    self.interface_call_5 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.INACTIVE)
    self.data_per_org_unit_EUS_5 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_5,
                                                                 org_unit=self.org_unit_EUS,
                                                                 active=False)
    self.contract_5_1 = StageContract.objects.create(contract_nr=123, contract_name="TESTING 123",
                                                     data_per_org_unit=self.data_per_org_unit_EUS_5, seq_nr=0)
    self.contract_5_2 = StageContract.objects.create(contract_nr=456, contract_name="TESTING 456",
                                                     data_per_org_unit=self.data_per_org_unit_EUS_5, seq_nr=1)


class ActivateDataPerOrgUnitTest(TestCase):

    def test_activate_and_deactivate_data_org_per_unit(self):

        setUpTeams(self)
        setUpNegometrixStaticData(self)
        setUpNegometrixInterfaceCall_5_InActive_EUS(self)

        self.assertEqual(self.data_per_org_unit_EUS_5.stagecontract_set.all().count(), 2)
        self.assertEqual(self.data_per_org_unit_EUS_5.contract_set.all().count(), 0)

        self.data_per_org_unit_EUS_5.activate()

        self.assertEqual(self.data_per_org_unit_EUS_5.contract_set.all().count(), 2)

        self.data_per_org_unit_EUS_5.deactivate()
        self.assertEqual(self.data_per_org_unit_EUS_5.contract_set.all().count(), 0)

    def test_activate_and_deactivate_interface_call(self):

        setUpTeams(self)
        setUpNegometrixStaticData(self)
        setUpNegometrixInterfaceCall_4_InActive_EUS_en_SITES(self)

        self.assertEqual(len(self.interface_call_4.stage_contracts()), 4)
        self.assertEqual(len(self.interface_call_4.contracts()), 0)

        self.interface_call_4.activate()

        self.assertEqual(len(self.interface_call_4.contracts()), 4)

        self.interface_call_4.deactivate()

        self.assertEqual(len(self.interface_call_4.contracts()), 0)


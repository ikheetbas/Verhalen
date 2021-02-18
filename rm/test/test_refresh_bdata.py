from django.db.models.functions import Now
from django.test import TestCase

from bdata.models import Contract
from rm.models import System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from stage.models import StageContract

from users.models import CustomUser, OrganizationalUnit
from .test_util import create_interface_call, add_data_per_org_unit
from ..constants import CONTRACTEN, NEGOMETRIX, FileStatus
from ..exceptions import DuplicateKeyException


def add_stage_contract(dpou: DataPerOrgUnit, seq_nr: int, contract_nr: str):
    return StageContract.objects.create(data_per_org_unit=dpou,
                                        contract_nr=contract_nr,
                                        seq_nr=seq_nr)

def add_contract(dpou: DataPerOrgUnit, seq_nr: int, contract_nr: str):
    return Contract.objects.create(data_per_org_unit=dpou,
                                   contract_nr=contract_nr,
                                   seq_nr=seq_nr)


class ActivateAndDeactivateTest(TestCase):

    def setUp(self):
        self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
        self.org_unit_EUS = OrganizationalUnit.objects.create(name="EUS", type=OrganizationalUnit.TEAM)

        self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition, created = InterfaceDefinition.objects.get_or_create(system=self.system,
                                                                       data_set_type=self.data_set_type,
                                                                       interface_type=InterfaceDefinition.UPLOAD)


    def test_activate_and_deactivate_interface_call(self):
        # PRE 1: InActive InterfaceCall with 2 inactive data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        dpou_IAAS = add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=False)
        dpou_EUS = add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_EUS, active=False)

        add_stage_contract(dpou=dpou_IAAS, seq_nr=0, contract_nr="123")
        add_stage_contract(dpou=dpou_IAAS, seq_nr=1, contract_nr="234")

        add_stage_contract(dpou=dpou_EUS, seq_nr=2, contract_nr="345")
        add_stage_contract(dpou=dpou_EUS, seq_nr=3, contract_nr="456")

        interface_call_1.activate_interface_call(start_transaction=True, cascading=True)

        self.assertEqual(interface_call_1.get_dataperorgunit("IAAS").contract_set.all().count(), 2)
        self.assertEqual(interface_call_1.get_dataperorgunit("EUS").contract_set.all().count(), 2)

        interface_call_1.deactivate_interface_call(start_transaction=True)
        self.assertEqual(interface_call_1.get_dataperorgunit("IAAS").contract_set.all().count(), 0)

    def test_activate_and_deactivate_dpou(self):
        # PRE 1: InActive InterfaceCall with 2 inactive data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        dpou_IAAS = add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=False)
        dpou_EUS = add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_EUS, active=False)

        add_stage_contract(dpou=dpou_IAAS, seq_nr=0, contract_nr="123")
        add_stage_contract(dpou=dpou_IAAS, seq_nr=1, contract_nr="234")

        add_stage_contract(dpou=dpou_EUS, seq_nr=2, contract_nr="345")
        add_stage_contract(dpou=dpou_EUS, seq_nr=3, contract_nr="456")

        interface_call_1.get_dataperorgunit("IAAS").activate_dataset(start_transaction=True)

        self.assertEqual(interface_call_1.get_dataperorgunit("IAAS").contract_set.all().count(), 2)
        self.assertEqual(interface_call_1.get_dataperorgunit("EUS").contract_set.all().count(), 0)

        interface_call_1.deactivate_interface_call(start_transaction=True)
        self.assertEqual(interface_call_1.get_dataperorgunit("IAAS").contract_set.all().count(), 0)

    def test_activate_call_with_dupkey_contractnr(self):
        # PRE 1: InActive InterfaceCall with 2 inactive data_per_org_unit, 1 with same key as Call 1
        interface_call_2: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        dpou_IAAS_2 = add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_IAAS, active=False)

        add_stage_contract(dpou=dpou_IAAS_2, seq_nr=0, contract_nr="123")
        add_stage_contract(dpou=dpou_IAAS_2, seq_nr=1, contract_nr="123")

        interface_call_2.activate_interface_call(start_transaction=True, cascading=True)
        interface_call_2.refresh_from_db()
        self.assertTrue("Duplicate Key" in interface_call_2.message, interface_call_2.message)
        self.assertEqual(interface_call_2.status, FileStatus.ERROR.name)

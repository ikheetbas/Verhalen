from django.db.models.functions import Now
from django.test import TestCase
from django.urls import reverse

from rm.interface_file import get_org_unit
from rm.models import Mapping, System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from stage.models import StageContract

from django.db.utils import IntegrityError

from users.models import CustomUser, OrganizationalUnit
from .test_util import set_up_user_with_interface_call_and_contract
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
    self.contract_5_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_5, seq_nr=0)
    self.contract_5_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_5, seq_nr=1)


class DeactivationTests(TestCase):

    def setUp(self):
        setUpNegometrixStaticData(self)
        setUpTeams(self)

        # InterfaceCall ACTIVE          IAAS en EUS
        setUpNegometrixInterfaceCall_1_Active_IAAS_en_EUS(self)
        # InterfaceCall INACTIVE        IAAS en EUS
        setUpNegometrixInterfaceCall_2_InActive_IAAS_en_EUS(self)

    def test_deactivate_active_data_per_org(self):
        """
        Stage_Contracts should not be removed when deactivating data_per_org_unit
        """
        # PRE CONDITION
        self.assertEqual(self.data_per_org_unit_IAAS_1.stagecontract_set.all().count(), 2)
        self.assertTrue(self.data_per_org_unit_IAAS_1.active)
        self.assertTrue(self.data_per_org_unit_EUS_1.active)

        self.data_per_org_unit_IAAS_1.deactivate()

        # POST: Only IAAS data is inactive, EUS is still active
        self.assertEqual(self.data_per_org_unit_IAAS_1.stagecontract_set.all().count(), 2)
        self.assertFalse(self.data_per_org_unit_IAAS_1.active)
        self.assertTrue(self.data_per_org_unit_EUS_1.active)

    def test_deactivate_data_per_org_unit_not_active(self):
        """
        If DataPerOrgUnit can be deactivated, als when it is already not active
        """
        self.data_per_org_unit_IAAS_1.active = False  # NOT NORMAL BEHAVIOR, JUST FOR TESTING
        self.assertEqual(self.data_per_org_unit_IAAS_1.stagecontract_set.all().count(), 2)

        self.data_per_org_unit_IAAS_1.deactivate()

        self.assertEqual(self.data_per_org_unit_IAAS_1.stagecontract_set.all().count(), 2)

    def test_deactivate_interface_call_happy_path(self):
        self.assertEqual(self.interface_call_1.stage_contracts().count(), 4)
        for data_per_org_unit in self.interface_call_1.dataperorgunit_set.all():
            data_per_org_unit.active = True

        self.interface_call_1.deactivate()

        self.assertEqual(self.interface_call_1.stage_contracts().count(), 4)
        self.assertFalse(self.interface_call_1.is_active())
        for data_per_org_unit in self.interface_call_1.dataperorgunit_set.all():
            self.assertFalse(data_per_org_unit.active)


class ActivationTestsWithSideEffects(TestCase):

    def setUp(self):
        setUpNegometrixStaticData(self)
        setUpTeams(self)

        # InterfaceCall ACTIVE          IAAS en EUS
        setUpNegometrixInterfaceCall_1_Active_IAAS_en_EUS(self)
        # InterfaceCall INACTIVE        IAAS en EUS
        setUpNegometrixInterfaceCall_2_InActive_IAAS_en_EUS(self)
        # InterfaceCall INACTIVE        IAAS en SITES
        setUpNegometrixInterfaceCall_3_InActive_IAAS_en_SITES(self)
        # InterfaceCall INACTIVE        EUS en SITES
        setUpNegometrixInterfaceCall_4_InActive_EUS_en_SITES(self)
        # InterfaceCall INACTIVE        EUS
        setUpNegometrixInterfaceCall_5_InActive_EUS(self)

    def test_activate_same_upload_as_previous(self):
        # PRE Interface 1 Active, 2 Inactive
        self.assertTrue(self.interface_call_1.is_active())
        self.assertFalse(self.interface_call_2.is_active())

        self.interface_call_2.activate()

        # POST interface call 1 INACTIVE
        self.interface_call_1.refresh_from_db()
        self.assertFalse(self.interface_call_1.is_active())
        for data_per_org_unit in self.interface_call_1.dataperorgunit_set.all():
            self.assertFalse(data_per_org_unit.active)

        # POST interface call 2 ACTIVE
        self.interface_call_2.refresh_from_db()
        assertInterfaceCallCompleteActive(self, True, self.interface_call_2)

    def test_activate_partly_same_upload_as_previous_deactivate_whole_previous_upload(self):
        # PRE Interface 1 Active, 3 Inactive
        self.assertTrue(self.interface_call_1.is_active())
        self.assertFalse(self.interface_call_3.is_active())

        self.interface_call_3.activate()

        # POST interface call 1 INACTIVE
        self.interface_call_1.refresh_from_db()
        assertInterfaceCallCompleteActive(self, False, self.interface_call_1)

        # POST interface call 3 ACTIVE
        self.interface_call_3.refresh_from_db()
        assertInterfaceCallCompleteActive(self, True, self.interface_call_3)

    def test_activate_partly_same_upload_as_previous_deactivate_two_previous_uploads(self):
        self.interface_call_3.activate()
        self.interface_call_5.activate()

        self.interface_call_1.refresh_from_db()
        self.interface_call_2.refresh_from_db()
        self.interface_call_3.refresh_from_db()
        self.interface_call_4.refresh_from_db()
        self.interface_call_5.refresh_from_db()

        assertInterfaceCallCompleteActive(self, False, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)
        assertInterfaceCallCompleteActive(self, True, self.interface_call_3)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_4)
        assertInterfaceCallCompleteActive(self, True, self.interface_call_5)

        self.interface_call_4.activate()

        self.interface_call_1.refresh_from_db()
        self.interface_call_2.refresh_from_db()
        self.interface_call_3.refresh_from_db()
        self.interface_call_4.refresh_from_db()
        self.interface_call_5.refresh_from_db()

        assertInterfaceCallCompleteActive(self, False, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_3)
        assertInterfaceCallCompleteActive(self, True, self.interface_call_4)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_5)


def assertInterfaceCallCompleteActive(self, active: bool, interface_call_1):
    """
    Assert that the InterfaceCall and its DataPerOrgUnits are all active or not
    """
    if active:
        self.assertTrue(interface_call_1.is_active())
        for data_per_org_unit in interface_call_1.dataperorgunit_set.all():
            self.assertTrue(data_per_org_unit.active)
    else:
        self.assertFalse(interface_call_1.is_active())
        for data_per_org_unit in interface_call_1.dataperorgunit_set.all():
            self.assertFalse(data_per_org_unit.active)


class ActivateWithoutSideEffects(TestCase):

    def setUp(self):
        setUpNegometrixStaticData(self)
        setUpTeams(self)

        # InterfaceCall ACTIVE          IAAS en EUS
        setUpNegometrixInterfaceCall_1_Active_IAAS_en_EUS(self)
        # InterfaceCall INACTIVE        IAAS en EUS
        setUpNegometrixInterfaceCall_2_InActive_IAAS_en_EUS(self)
        # InterfaceCall INACTIVE        IAAS en SITES
        setUpNegometrixInterfaceCall_3_InActive_IAAS_en_SITES(self)
        # InterfaceCall INACTIVE        EUS en SITES
        setUpNegometrixInterfaceCall_4_InActive_EUS_en_SITES(self)
        # InterfaceCall INACTIVE        EUS
        setUpNegometrixInterfaceCall_5_InActive_EUS(self)

    def test_activate_data_per_org_unit_with_active_sibling(self):
        # PRE: 1 is actief, 2 niet
        assertInterfaceCallCompleteActive(self, True, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

        # Try to activate a DataOrg of 2, should give error
        with self.assertRaises(SystemError):
            self.data_per_org_unit_IAAS_2.activate()

        # POST: Nothing changed
        assertInterfaceCallCompleteActive(self, True, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

    def test_deactivate_whole_int_call(self):
        # PRE: 1 is actief, 2 niet
        assertInterfaceCallCompleteActive(self, True, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

        # Deactivate 1
        self.interface_call_1.deactivate()

        # POST: 1 & 2 both NOT active
        assertInterfaceCallCompleteActive(self, False, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

        # Now activate a single DataOrg of 2
        self.data_per_org_unit_IAAS_2.activate()

        # POST: Interface Call 2 still NOT active,
        #       data_per_org_unit_IAAS_2 Active,
        #       data_per_org_unit_EUS_2 still NOT active
        self.assertTrue(not self.interface_call_2.is_active())
        self.assertTrue(    self.data_per_org_unit_IAAS_2.active)
        self.assertTrue(not self.data_per_org_unit_EUS_2.active)

        # Now make InterfaceCall 1 active,
        self.interface_call_1.activate()
        # Which must make interface_call_2 (with data_per_org_unit_IAAS_2) complete Inactive again
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)


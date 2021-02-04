from django.db import IntegrityError, transaction
from django.db.models.functions import Now
from django.test import TestCase

from bdata.models import Contract
from rm.models import Mapping, System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from stage.models import StageContract

from users.models import CustomUser, OrganizationalUnit
from ..constants import CONTRACTEN, NEGOMETRIX
from ..exceptions import DuplicateKeyException, OtherActiveDataPerOrgUnitException


def setUpTeams(self):
    self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
    self.org_unit_EUS = OrganizationalUnit.objects.create(name="EUS", type=OrganizationalUnit.TEAM)
    self.org_unit_SITES = OrganizationalUnit.objects.create(name="SITES", type=OrganizationalUnit.TEAM)
    self.org_unit_XXX = OrganizationalUnit.objects.create(name="XXX", type=OrganizationalUnit.TEAM)
    self.org_unit_YYY = OrganizationalUnit.objects.create(name="YYY", type=OrganizationalUnit.TEAM)
    self.org_unit_ZZZ = OrganizationalUnit.objects.create(name="ZZZ", type=OrganizationalUnit.TEAM)


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


def setUpNegometrixInterfaceCall_4_InActive_EUS_en_SITES_with_dupl_contract_nr(self):
    self.interface_call_4 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.INACTIVE)
    self.data_per_org_unit_EUS_4 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_4,
                                                                 org_unit=self.org_unit_EUS,
                                                                 active=False)
    self.contract_4_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_4, seq_nr=0,
                                                     contract_nr=41)
    self.contract_4_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_4, seq_nr=1,
                                                     contract_nr=41)

    self.data_per_org_unit_SITES_4 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_4,
                                                                   org_unit=self.org_unit_SITES,
                                                                   active=False)
    self.contract_4_3 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_SITES_4, seq_nr=2,
                                                     contract_nr=43)
    self.contract_4_4 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_SITES_4, seq_nr=3,
                                                     contract_nr=41)


def setUpNegometrixInterfaceCall_5_InActive_EUS(self):
    self.interface_call_5 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.INACTIVE)
    self.data_per_org_unit_EUS_5 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_5,
                                                                 org_unit=self.org_unit_EUS,
                                                                 active=False)
    self.contract_5_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_5, seq_nr=0)
    self.contract_5_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_5, seq_nr=1)


def setUpNegometrixInterfaceCall_6_InActive_XXX_en_YYY(self):
    self.interface_call_6 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.INACTIVE)
    self.data_per_org_unit_XXX_6 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_6,
                                                                 org_unit=self.org_unit_XXX,
                                                                 active=False)
    self.contract_6_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_XXX_6, seq_nr=0,
                                                     contract_nr=1)
    self.contract_6_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_XXX_6, seq_nr=1,
                                                     contract_nr=2)

    self.data_per_org_unit_YYY_6 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_6,
                                                                 org_unit=self.org_unit_YYY,
                                                                 active=False)
    self.contract_6_3 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_YYY_6, seq_nr=2,
                                                     contract_nr=3)
    self.contract_6_4 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_YYY_6, seq_nr=3,
                                                     contract_nr=4)


def setUpNegometrixInterfaceCall_7_InActive_EUS_en_SITES_with_correct_contract_nr(self):
    self.interface_call_7 = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                         date_time_creation=Now(),
                                                         status=InterfaceCall.INACTIVE)

    self.data_per_org_unit_EUS_7 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_7,
                                                                 org_unit=self.org_unit_EUS,
                                                                 active=False)
    self.contract_7_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_7, seq_nr=0,
                                                     contract_nr=41)
    self.contract_7_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_EUS_7, seq_nr=1,
                                                     contract_nr=42)

    self.data_per_org_unit_SITES_7 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_7,
                                                                   org_unit=self.org_unit_SITES,
                                                                   active=False)
    self.contract_7_3 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_SITES_7, seq_nr=2,
                                                     contract_nr=43)
    self.contract_7_4 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_SITES_7, seq_nr=3,
                                                     contract_nr=44)


def setUpNegometrixInterfaceCall_8_InActive_ZZZ(self):
    self.interface_call_8_Inactive_ZZZ_with_dupl = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                                                date_time_creation=Now(),
                                                                                status=InterfaceCall.INACTIVE)
    self.data_per_org_unit_ZZZ_8 = DataPerOrgUnit.objects.create(interface_call=self.interface_call_8_Inactive_ZZZ_with_dupl,
                                                                 org_unit=self.org_unit_ZZZ,
                                                                 active=False)
    self.contract_8_1 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_ZZZ_8, seq_nr=0, contract_nr=1)
    self.contract_8_2 = StageContract.objects.create(data_per_org_unit=self.data_per_org_unit_ZZZ_8, seq_nr=1, contract_nr=1)

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

        self.data_per_org_unit_IAAS_1.deactivate_dataset()

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

        self.data_per_org_unit_IAAS_1.deactivate_dataset()

        self.assertEqual(self.data_per_org_unit_IAAS_1.stagecontract_set.all().count(), 2)

    def test_deactivate_interface_call_happy_path(self):
        self.assertEqual(self.interface_call_1.stage_contracts().count(), 4)
        for data_per_org_unit in self.interface_call_1.dataperorgunit_set.all():
            data_per_org_unit.active = True

        self.interface_call_1.deactivate_interface_call()

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
        setUpNegometrixInterfaceCall_4_InActive_EUS_en_SITES_with_dupl_contract_nr(self)
        # InterfaceCall INACTIVE        EUS
        setUpNegometrixInterfaceCall_5_InActive_EUS(self)

        setUpNegometrixInterfaceCall_7_InActive_EUS_en_SITES_with_correct_contract_nr(self)

    def test_activate_same_upload_as_previous(self):
        # PRE Interface 1 Active, 2 Inactive
        self.assertTrue(self.interface_call_1.is_active())
        self.assertFalse(self.interface_call_2.is_active())

        self.interface_call_2.activate_interface_call()

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

        self.interface_call_3.activate_interface_call()

        # POST interface call 1 INACTIVE
        self.interface_call_1.refresh_from_db()
        assertInterfaceCallCompleteActive(self, False, self.interface_call_1)

        # POST interface call 3 ACTIVE
        self.interface_call_3.refresh_from_db()
        assertInterfaceCallCompleteActive(self, True, self.interface_call_3)

    def test_activate_partly_same_upload_as_previous_deactivate_two_previous_uploads(self):
        self.interface_call_3.activate_interface_call()
        self.interface_call_5.activate_interface_call()

        self.interface_call_1.refresh_from_db()
        self.interface_call_2.refresh_from_db()
        self.interface_call_3.refresh_from_db()
        self.interface_call_7.refresh_from_db()
        self.interface_call_5.refresh_from_db()

        assertInterfaceCallCompleteActive(self, False, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)
        assertInterfaceCallCompleteActive(self, True, self.interface_call_3)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_7)
        assertInterfaceCallCompleteActive(self, True, self.interface_call_5)

        self.interface_call_7.activate_interface_call()

        self.interface_call_1.refresh_from_db()
        self.interface_call_2.refresh_from_db()
        self.interface_call_3.refresh_from_db()
        self.interface_call_7.refresh_from_db()
        self.interface_call_5.refresh_from_db()

        assertInterfaceCallCompleteActive(self, False, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_3)
        assertInterfaceCallCompleteActive(self, True, self.interface_call_7)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_5)


def assertInterfaceCallCompleteActive(self, active: bool, interface_call):
    """
    Assert that the InterfaceCall and its DataPerOrgUnits are all active or not
    """
    if active:
        self.assertTrue(interface_call.is_active())
        for data_per_org_unit in interface_call.dataperorgunit_set.all():
            self.assertTrue(data_per_org_unit.active)
    else:
        self.assertFalse(interface_call.is_active())
        for data_per_org_unit in interface_call.dataperorgunit_set.all():
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
        setUpNegometrixInterfaceCall_4_InActive_EUS_en_SITES_with_dupl_contract_nr(self)
        # InterfaceCall INACTIVE        EUS
        setUpNegometrixInterfaceCall_5_InActive_EUS(self)
        # InterfaceCall INACTIVE        XXX en YYY
        setUpNegometrixInterfaceCall_6_InActive_XXX_en_YYY(self)

    def test_activate_data_per_org_unit_with_active_sibling(self):
        # PRE: 1 is actief, 2 niet
        assertInterfaceCallCompleteActive(self, True, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

        # Try to activate a DataOrg of 2, should give error
        with self.assertRaises(OtherActiveDataPerOrgUnitException):
            self.data_per_org_unit_IAAS_2.activate_dataset()

        # POST: Nothing changed
        assertInterfaceCallCompleteActive(self, True, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

    def test_deactivate_whole_int_call(self):
        # PRE: 1 is actief, 2 niet
        assertInterfaceCallCompleteActive(self, True, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

        # Deactivate 1
        self.interface_call_1.deactivate_interface_call()

        # POST: 1 & 2 both NOT active
        assertInterfaceCallCompleteActive(self, False, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

        # Now activate a single DataOrg of 2
        self.data_per_org_unit_IAAS_2.activate_dataset()

        # POST: Interface Call 2 still NOT active,
        #       data_per_org_unit_IAAS_2 Active,
        #       data_per_org_unit_EUS_2 still NOT active
        self.assertTrue(not self.interface_call_2.is_active())
        self.assertTrue(self.data_per_org_unit_IAAS_2.active)
        self.assertTrue(not self.data_per_org_unit_EUS_2.active)

        # Now make InterfaceCall 1 active,
        self.interface_call_1.activate_interface_call()
        # Which must make interface_call_2 (with data_per_org_unit_IAAS_2) complete Inactive again
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

    def test_check_on_all_data_per_org_unit_are_inactive_True(self):
        # PRE: interface call 2 is complete deactive
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)

        self.assertTrue(self.interface_call_2.dataperorgunit_set.all()[0].
                        all_data_org_units_of_this_interface_call_are_inactive())

    def test_check_on_all_data_per_org_unit_are_inactive_True(self):
        # PRE: interface call 2 is complete inactive
        assertInterfaceCallCompleteActive(self, False, self.interface_call_6)
        self.assertTrue(self.interface_call_6.dataperorgunit_set.all()[0].
                        all_data_org_units_of_this_interface_call_are_inactive())

        # ACTION: activate one on the data_per_org_units
        self.interface_call_6.dataperorgunit_set.all()[0].activate_dataset()

        # POST: not all data_per_org_units are inactive
        self.assertFalse(self.interface_call_6.dataperorgunit_set.all()[0].
                         all_data_org_units_of_this_interface_call_are_inactive())

    def test_deactivate_last_active_data_per_org_unit_of_interface_call(self):
        # PRE: Active Interface_call with two active data-per-org_units
        assertInterfaceCallCompleteActive(self, True, self.interface_call_1)
        self.assertEqual(self.interface_call_1.dataperorgunit_set.all().count(), 2)

        # ACTIE 1: de-activate 1 data_per_org_unit
        self.interface_call_1.dataperorgunit_set.all()[0].deactivate_dataset()

        # POST 1: interface_call still active
        self.assertEqual(True, self.interface_call_1.is_active())

        # ACTIE 2: de-activate 2nd data_per_org_unit
        self.interface_call_1.dataperorgunit_set.all()[1].deactivate_dataset()

        # POST 1: interface_call now inactive
        self.assertEqual(False, self.interface_call_1.is_active())

    def test_activate_last_inactive_data_per_org_unit_of_interface_call(self):
        # PRE: Active Interface_call with two active data-per-org_units
        assertInterfaceCallCompleteActive(self, False, self.interface_call_6)
        self.assertEqual(self.interface_call_6.dataperorgunit_set.all().count(), 2)

        # ACTIE 1: activate 1 data_per_org_unit
        self.interface_call_6.dataperorgunit_set.all()[0].activate_dataset()

        # POST 1: interface_call still inactive
        self.assertEqual(False, self.interface_call_6.is_active())

        # ACTIE 2: activate 2nd data_per_org_unit
        self.interface_call_6.dataperorgunit_set.all()[1].activate_dataset()

        # POST 1: interface_call now active
        self.assertEqual(True, self.interface_call_6.is_active())

    def test_activeren_data_per_org_unit_with_active_other_one(self):
        # PRE: interface call 1 is total active, 2 is inactive and have a IAAS dataset for Contracten
        assertInterfaceCallCompleteActive(self, True, self.interface_call_1)
        assertInterfaceCallCompleteActive(self, False, self.interface_call_2)
        self.assertEqual(self.interface_call_1.dataperorgunit_set.all()[0].get_data_set_type(),
                         self.interface_call_2.dataperorgunit_set.all()[0].get_data_set_type())

        # ACTION: activate the inactive datasetperorgunit, which should raise an exception
        with self.assertRaises(OtherActiveDataPerOrgUnitException):
            self.interface_call_2.dataperorgunit_set.all()[0].activate_dataset()

        # ACTION 2: Now deactivate the active dataperorgunit
        self.interface_call_1.dataperorgunit_set.all()[0].deactivate_dataset()

        # ACTION 3: Now activating should succeed
        self.interface_call_2.dataperorgunit_set.all()[0].activate_dataset()

        # POST: and it must be active now
        self.assertTrue(self.interface_call_2.dataperorgunit_set.all()[0].active)


class RefreshContractDataTests(TestCase):

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
        setUpNegometrixInterfaceCall_4_InActive_EUS_en_SITES_with_dupl_contract_nr(self)
        # InterfaceCall INACTIVE        EUS
        setUpNegometrixInterfaceCall_5_InActive_EUS(self)
        # InterfaceCall INACTIVE        XXX en YYY
        setUpNegometrixInterfaceCall_6_InActive_XXX_en_YYY(self)
        # InterfaceCall INACTIVE        ZZZ
        setUpNegometrixInterfaceCall_8_InActive_ZZZ(self)

    def test_amount_of_contracts_copied_and_removed(self):

        # PREPARATION
        self.interface_call_1.deactivate_interface_call()

        # PRE: no Contracts
        self.assertEqual(Contract.objects.all().count(), 0)

        # ACTION: activate Interface Call 1
        self.interface_call_1.activate_interface_call()

        # POST: 4 Contracts
        self.assertEqual(Contract.objects.all().count(), 4)

        # ACTION 2: deactivate again
        self.interface_call_1.deactivate_interface_call()

        # POST: no Contracts
        self.assertEqual(Contract.objects.all().count(), 0)

    def test_exception_and_rollback_for_dupkey_contractnr_when_activating_data_per_org_unit(self):

        # POST: interface_call has 4 StageContracts
        self.assertEqual(len(self.interface_call_8_Inactive_ZZZ_with_dupl.stage_contracts()), 2)

        # ACTION: activate the second, creating Contracts with same contract_nr, resulting in an Duplicate
        try:
            with transaction.atomic():
                self.interface_call_8_Inactive_ZZZ_with_dupl.dataperorgunit_set.all()[0].activate_dataset(start_transaction=True)
            self.fail("Expected Duplicate exception here")
        except DuplicateKeyException as ex:
            print(f"Expected DuplicateKeyException, and it was indeed :-) Exception details: {ex.__str__()}")
        except Exception as ex:
            self.fail(f"Expected Duplicate exception here, but got a: {ex.__str__()}")

        # POST: dataperorgunit still inactive and no contracts
        self.assertEqual(False, self.interface_call_8_Inactive_ZZZ_with_dupl.dataperorgunit_set.all()[0].active)
        self.assertEqual(0, self.interface_call_8_Inactive_ZZZ_with_dupl.dataperorgunit_set.all()[0].contract_set.all().count())

    def test_exception_and_rollback_for_dupkey_contractnr_when_activating_interface_call(self):

        # POST: interface_call has 4 StageContracts
        self.assertEqual(len(self.interface_call_4.stage_contracts()), 4)
        self.assertEqual(len(self.interface_call_4.contracts()), 0)

        # ACTION: activate the second, creating Contracts with same contract_nr, resulting in an Duplicate
        try:
            with transaction.atomic():
                self.interface_call_4.activate_interface_call(start_transaction=True)
            self.fail("Expected Duplicate exception here, but there wasn't")
        except DuplicateKeyException as ex:
            print(f"Expected DuplicateKeyException, and it was indeed :-) Exception details: {ex.__str__()}")
        except Exception as ex:
            self.fail(f"Expected Duplicate exception here, but got a: {ex.__str__()}")

        # POST: dataperorgunit still inactive and no contracts
        assertInterfaceCallCompleteActive(self, False, self.interface_call_4)
        self.assertEqual(0, len(self.interface_call_4.contracts()))

from django.test import TestCase

import users
from rm.constants import NEGOMETRIX, CONTRACTEN
from rm.models import System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from rm.test.test_util import add_data_per_org_unit, create_interface_call
from users.models import OrganizationalUnit


class IsCompletelyActiveInactiveTests(TestCase):

    def setUp(self):
        self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.create(system=self.system,
                                                                       data_set_type=self.data_set_type,
                                                                       interface_type=InterfaceDefinition.UPLOAD)
        self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
        self.org_unit_EUS = OrganizationalUnit.objects.create(name="EUS", type=OrganizationalUnit.TEAM)

    def test_interface_call_active(self):
        interface_call: InterfaceCall = create_interface_call(active=True,
                                                              interface_definition=self.interface_definition)
        self.assertTrue(interface_call.is_completely_active())

    def test_interface_call_inactive(self):
        interface_call: InterfaceCall = create_interface_call(active=False,
                                                              interface_definition=self.interface_definition)
        self.assertTrue(interface_call.is_completely_inactive())

    def test_interface_call_with_dpou_active(self):
        interface_call: InterfaceCall = create_interface_call(active=True,
                                                              interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_IAAS, active=True)
        self.assertTrue(interface_call.is_completely_active())

    def test_interface_call_with_dpou_inactive(self):
        interface_call: InterfaceCall = create_interface_call(active=False,
                                                              interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_IAAS, active=False)
        self.assertTrue(interface_call.is_completely_inactive())

    def test_active_interface_call_with_inactive_dpou(self):
        interface_call: InterfaceCall = create_interface_call(active=True,
                                                              interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_IAAS, active=False)
        self.assertFalse(interface_call.is_completely_active())
        self.assertFalse(interface_call.is_completely_inactive())

    def test_inactive_interface_call_with_active_dpou(self):
        interface_call: InterfaceCall = create_interface_call(active=False,
                                                              interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_IAAS, active=True)
        self.assertFalse(interface_call.is_completely_active())
        self.assertFalse(interface_call.is_completely_inactive())

    def test_active_interface_call_with_active_and_inactive_dpou(self):
        interface_call: InterfaceCall = create_interface_call(active=True,
                                                              interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_IAAS, active=True)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_EUS, active=False)
        self.assertFalse(interface_call.is_completely_active())
        self.assertFalse(interface_call.is_completely_inactive())

    def test_inactive_interface_call_with_active_and_inactive_dpou(self):
        interface_call: InterfaceCall = create_interface_call(active=False,
                                                              interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_IAAS, active=True)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_EUS, active=False)
        self.assertFalse(interface_call.is_completely_active())
        self.assertFalse(interface_call.is_completely_inactive())

class GetDataPerOrgUnitTests(TestCase):

    def setUp(self):
        self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
        self.org_unit_XXX = OrganizationalUnit.objects.create(name="XXX", type=OrganizationalUnit.TEAM)
        self.org_unit_YYY = OrganizationalUnit.objects.create(name="YYY", type=OrganizationalUnit.TEAM)
        self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.create(system=self.system,
                                                                       data_set_type=self.data_set_type,
                                                                       interface_type=InterfaceDefinition.UPLOAD)
        self.interface_call: InterfaceCall = create_interface_call(active=False,
                                                                   interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=self.interface_call, org_unit=self.org_unit_XXX, active=False)
        add_data_per_org_unit(interface_call=self.interface_call, org_unit=self.org_unit_YYY, active=False)

    def test_get_dataperorgunit_with_none(self):

        with self.assertRaises(ValueError):
            self.interface_call.get_dataperorgunit(None)

    def test_get_dataperorgunit_with_correct_string(self):
        dataperorgunit_XXX: DataPerOrgUnit = self.interface_call.get_dataperorgunit("XXX")
        self.assertEqual(dataperorgunit_XXX.org_unit.name, "XXX")

    def test_get_dataperorgunit_with_incorrect_string(self):
        with self.assertRaises(users.models.OrganizationalUnit.DoesNotExist):
            self.interface_call.get_dataperorgunit("XYZ")

    def test_get_dataperorgunit_with_correct_org_unit(self):
        dataperorgunit_XXX: DataPerOrgUnit = self.interface_call.get_dataperorgunit(self.org_unit_XXX)
        self.assertEqual(dataperorgunit_XXX.org_unit.name, "XXX")

    def test_get_dataperorgunit_with_incorrect_org_unit(self):
        with self.assertRaises(users.models.OrganizationalUnit.DoesNotExist):
            self.interface_call.get_dataperorgunit(self.org_unit_IAAS)


class ActivateInterfaceCallTests(TestCase):

    def setUp(self):

        self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
        self.org_unit_EUS = OrganizationalUnit.objects.create(name="EUS", type=OrganizationalUnit.TEAM)
        self.org_unit_SITES = OrganizationalUnit.objects.create(name="SITES", type=OrganizationalUnit.TEAM)
        self.org_unit_XXX = OrganizationalUnit.objects.create(name="XXX", type=OrganizationalUnit.TEAM)
        self.org_unit_YYY = OrganizationalUnit.objects.create(name="YYY", type=OrganizationalUnit.TEAM)
        self.org_unit_ZZZ = OrganizationalUnit.objects.create(name="ZZZ", type=OrganizationalUnit.TEAM)

        self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.create(system=self.system,
                                                                       data_set_type=self.data_set_type,
                                                                       interface_type=InterfaceDefinition.UPLOAD)

    def test_1_activate_simple_interface_call(self):

        # PRE: InActive InterfaceCall with 1 inactive data_per_org_unit
        interface_call: InterfaceCall = create_interface_call(active=False,
                                                              interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call, org_unit=self.org_unit_IAAS, active=False)

        self.assertTrue(interface_call.is_completely_inactive())

        # ACTION: activate interface_call
        interface_call.activate_interface_call(start_transaction=True, cascading=True)

        # POST: interface_call with data_per_org-unit is active
        self.assertTrue(interface_call.is_completely_active())


    def test_2_activate_simpel_interface_call_deactivate_other_simple(self):

        # PRE 1: InActive InterfaceCall with 1 inactive data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=False)

        # PRE 2: Active InterfaceCall with 1 active data_per_org_unit
        interface_call_2: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_IAAS, active=True)

        # PRE CHECK: 1 is InActive, 2 is active
        self.assertTrue(interface_call_1.is_completely_inactive())
        self.assertTrue(interface_call_2.is_completely_active())

        # ACTION: activate interface_call
        interface_call_1.activate_interface_call(start_transaction=True, cascading=True)

        # POST: 1 is active, 2 is InActive
        interface_call_1.refresh_from_db()
        self.assertTrue(interface_call_1.is_completely_active())

        interface_call_2.refresh_from_db()
        self.assertTrue(interface_call_2.is_completely_inactive())



    def test_3_activate_interface_call_X_Y_deactivate_2_others_one_with_X_other_with_Y(self):

        # PRE 1: InActive InterfaceCall with 2 inactive data_per_org_unit, X and Y
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_XXX, active=False)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_YYY, active=False)

        # PRE 2: Active InterfaceCall with X org_unit
        interface_call_2: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_XXX, active=True)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_IAAS, active=True)

        # PRE 3: Active InterfaceCall with XY org_unit
        interface_call_3: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_3, org_unit=self.org_unit_YYY, active=True)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_EUS, active=True)

        # PRE CHECK: 1 is InActive, 2 is active
        self.assertTrue(interface_call_1.is_completely_inactive())
        self.assertTrue(interface_call_2.is_completely_active())
        self.assertTrue(interface_call_3.is_completely_active())

        # ACTION: activate interface_call
        interface_call_1.activate_interface_call(start_transaction=True, cascading=True)

        # POST 1: 1 is active
        interface_call_1.refresh_from_db()
        self.assertTrue(interface_call_1.is_completely_active())

        # POST 2: Both call 2 & 3 are COMPLETELY inactive!
        interface_call_2.refresh_from_db()
        self.assertTrue(interface_call_2.is_completely_inactive())
        interface_call_3.refresh_from_db()
        self.assertTrue(interface_call_3.is_completely_inactive())

    def test_4_activate_active_call_with_some_inactive_dpou(self):
        # PRE 2: Active InterfaceCall with X org_unit
        interface_call_2: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_XXX, active=False)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_IAAS, active=True)

        interface_call_2.activate_interface_call(start_transaction=True, cascading=True)

        interface_call_2.refresh_from_db()
        self.assertTrue(interface_call_2.active)
        self.assertTrue(interface_call_2.get_dataperorgunit("XXX").active)
        self.assertTrue(interface_call_2.get_dataperorgunit("IAAS").active)

class ActivateDataPerOrgUnitTests(TestCase):

    def setUp(self):
        self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
        self.org_unit_EUS = OrganizationalUnit.objects.create(name="EUS", type=OrganizationalUnit.TEAM)

        self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.create(system=self.system,
                                                                       data_set_type=self.data_set_type,
                                                                       interface_type=InterfaceDefinition.UPLOAD)

    def test_1_activate_single_dpou(self):
        # PRE 1: InActive InterfaceCall with 1 inactive data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=False)

        # ACTION: activate the DPOU
        interface_call_1.dataperorgunit_set.all()[0].activate_dataset(start_transaction=True)

        # POST: activating the only DPOU should make the whole call active
        self.assertTrue(interface_call_1.is_completely_active())

    def test_2_activate_one_of_two_inactive_dpou(self):
        # PRE 1: InActive InterfaceCall with 1 inactive data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=False)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_EUS, active=False)

        # ACTION: activate the DPOU
        interface_call_1.dataperorgunit_set.all()[0].activate_dataset(start_transaction=True)

        # POST: activating the only DPOU should make the whole call active
        self.assertTrue(interface_call_1.is_active())
        self.assertTrue(interface_call_1.dataperorgunit_set.all()[0].active)
        self.assertTrue(interface_call_1.dataperorgunit_set.all()[1].not_active)

        # ACTION: activate the other DPOU
        interface_call_1.dataperorgunit_set.all()[1].activate_dataset()
        self.assertTrue(interface_call_1.is_completely_active())

    def test_3_activate_DPOU_with_deactivating_other_with_only_one_DPOU(self):
        # PRE 1: InActive InterfaceCall with 1 inactive data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=False)

        # PRE 2: Active InterfaceCall with 1 active data_per_org_unit
        interface_call_2: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_IAAS, active=True)

        # ACTION activate the DPOU 2
        interface_call_1.dataperorgunit_set.all()[0].activate_dataset(start_transaction=True)

        # POST
        interface_call_1.refresh_from_db()
        self.assertTrue(interface_call_1.is_completely_active())
        interface_call_2.refresh_from_db()
        self.assertTrue(interface_call_2.is_completely_inactive())

    def test_4_activate_DPOU_with_deactivating_other_with_two_active_DPOU(self):
        # PRE 1: InActive InterfaceCall with 1 inactive data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=False)

        # PRE 2: Active InterfaceCall with 1 active data_per_org_unit
        interface_call_2: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_IAAS, active=True)
        add_data_per_org_unit(interface_call=interface_call_2, org_unit=self.org_unit_EUS, active=True)

        # ACTION activate the DPOU 2
        interface_call_1.get_dataperorgunit(self.org_unit_IAAS).activate_dataset(start_transaction=True)

        # POST Call 1 is completely active
        interface_call_1.refresh_from_db()
        self.assertTrue(interface_call_1.is_completely_active())

        # POST Call 2 is active, but not complete, only DPOU EUS is active
        interface_call_2.refresh_from_db()
        self.assertTrue(interface_call_2.is_active())
        self.assertTrue(interface_call_2.get_dataperorgunit(self.org_unit_IAAS).not_active)
        self.assertTrue(interface_call_2.get_dataperorgunit(self.org_unit_EUS).active)

    def test_5_activate_one_dpou_from_more(self):

        # PRE 1: InActive InterfaceCall with 2 inactive data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=False,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=False)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_EUS, active=False)

        # ACTION: activate 1
        interface_call_1.get_dataperorgunit(self.org_unit_IAAS).activate_dataset(start_transaction=True)

        # POST Call is active, dpou_1 IAAS is active, EUS still inactive
        self.assertTrue(interface_call_1.active)
        self.assertTrue(interface_call_1.get_dataperorgunit("IAAS").active)
        self.assertTrue(interface_call_1.get_dataperorgunit("EUS").not_active)



class DeactivateInterfaceCallTests(TestCase):

    def setUp(self):
        self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
        self.org_unit_EUS = OrganizationalUnit.objects.create(name="EUS", type=OrganizationalUnit.TEAM)

        self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.create(system=self.system,
                                                                       data_set_type=self.data_set_type,
                                                                       interface_type=InterfaceDefinition.UPLOAD)

    def test_1_call_with_one_dpou(self):
        # PRE 1: Active InterfaceCall with 1 active data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=True)

        interface_call_1.deactivate_interface_call(start_transaction=True)

        self.assertTrue(interface_call_1.not_active)
        self.assertTrue(interface_call_1.get_dataperorgunit("IAAS").not_active)

    def test_2_call_with_two_dpou(self):
        # PRE 1: Active InterfaceCall with 2 active data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=True)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_EUS, active=True)

        interface_call_1.deactivate_interface_call(start_transaction=True)

        self.assertTrue(interface_call_1.not_active)
        self.assertTrue(interface_call_1.get_dataperorgunit("IAAS").not_active)
        self.assertTrue(interface_call_1.get_dataperorgunit("EUS").not_active)

    def test_3_active_call_with_one_active_one_inactive_dpou(self):
        # PRE 1: Active InterfaceCall with 2 active data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=True)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_EUS, active=False)

        interface_call_1.deactivate_interface_call(start_transaction=True)

        self.assertTrue(interface_call_1.not_active)
        self.assertTrue(interface_call_1.get_dataperorgunit("IAAS").not_active)
        self.assertTrue(interface_call_1.get_dataperorgunit("EUS").not_active)


class DeactivateDataPerOrgUnitTest(TestCase):

    def setUp(self):
        self.org_unit_IAAS = OrganizationalUnit.objects.create(name="IAAS", type=OrganizationalUnit.TEAM)
        self.org_unit_EUS = OrganizationalUnit.objects.create(name="EUS", type=OrganizationalUnit.TEAM)

        self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.create(system=self.system,
                                                                       data_set_type=self.data_set_type,
                                                                       interface_type=InterfaceDefinition.UPLOAD)
    def test_1_deactivate_only_dpou_of_a_call(self):
        # PRE 1: Active InterfaceCall with 1 active data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=True)

        interface_call_1.get_dataperorgunit("IAAS").deactivate_dataset(start_transaction=True)

        self.assertTrue(interface_call_1.not_active)
        self.assertTrue(interface_call_1.get_dataperorgunit("IAAS").not_active)

    def test_2_deactivate_one_of_two_active_dpou_in_one_call(self):
        # PRE 1: Active InterfaceCall with 2 active data_per_org_unit
        interface_call_1: InterfaceCall = create_interface_call(active=True,
                                                                interface_definition=self.interface_definition)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_IAAS, active=True)
        add_data_per_org_unit(interface_call=interface_call_1, org_unit=self.org_unit_EUS, active=True)

        interface_call_1.get_dataperorgunit("IAAS").deactivate_dataset(start_transaction=True)

        self.assertTrue(interface_call_1.active)
        self.assertTrue(interface_call_1.get_dataperorgunit("IAAS").not_active)
        self.assertTrue(interface_call_1.get_dataperorgunit("EUS").active)

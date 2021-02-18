from django.test import TestCase

from rm.constants import CONTRACTEN, RowStatus
from rm.models import System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from rm.test.test_util import set_up_user_with_interface_call_and_contract
from users.models import OrganizationalUnit


class DataPerOrgUnitTest(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self)

    def test_get_data_set_type_happy(self):
        data_set_type = self.data_per_org_unit.get_data_set_type()
        self.assertIsNotNone(data_set_type)
        self.assertIsNotNone(data_set_type.name)
        self.assertEqual(data_set_type.name, CONTRACTEN)

    def test_check_active_happy_and_unhappy(self):
        system_y = System.objects.create(name="SYSTEM_Y")
        data_set_type_y = DataSetType.objects.create(name="DATA_Y")
        org_unit_y = OrganizationalUnit.objects.create(name="AFDELING_Y",
                                                       type=OrganizationalUnit.TEAM)
        interface_def_y = InterfaceDefinition.objects.create(name="INTERFACE_Y",
                                                             system=system_y,
                                                             data_set_type=data_set_type_y,
                                                             interface_type=InterfaceDefinition.UPLOAD)
        interface_call_y = InterfaceCall.objects.create(interface_definition=interface_def_y)
        data_per_org_unit_y = DataPerOrgUnit.objects.create(org_unit=org_unit_y,
                                                            interface_call=interface_call_y,
                                                            active=True)

        self.assertTrue(data_per_org_unit_y.active)

    def test_increase_row_count_ok(self):
        system_y = System.objects.create(name="SYSTEM_Y")
        data_set_type_y = DataSetType.objects.create(name="DATA_Y")
        org_unit_y = OrganizationalUnit.objects.create(name="AFDELING_Y",
                                                       type=OrganizationalUnit.TEAM)
        interface_def_y = InterfaceDefinition.objects.create(name="INTERFACE_Y",
                                                             system=system_y,
                                                             data_set_type=data_set_type_y,
                                                             interface_type=InterfaceDefinition.UPLOAD)
        interface_call_y = InterfaceCall.objects.create(interface_definition=interface_def_y)
        dpou = DataPerOrgUnit.objects.create(org_unit=org_unit_y,
                                                            interface_call=interface_call_y,
                                                            active=True)

        self.assertEqual(dpou.number_of_data_rows_ok, 0)
        self.assertEqual(dpou.number_of_data_rows_warning, 0)

        dpou.increase_row_count(1, RowStatus.DATA_OK)
        self.assertEqual(dpou.number_of_data_rows_ok, 1)
        self.assertEqual(dpou.number_of_data_rows_warning, 0)

        dpou.increase_row_count(1, RowStatus.DATA_WARNING)
        self.assertEqual(dpou.number_of_data_rows_ok, 1)
        self.assertEqual(dpou.number_of_data_rows_warning, 1)

        with self.assertRaises(ValueError):
            dpou.increase_row_count(1, RowStatus.EMPTY_ROW)
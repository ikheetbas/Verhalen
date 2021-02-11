from django.test import TestCase

from rm.interface_file import get_org_unit
from rm.models import Mapping, System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from stage.models import StageContract

from users.models import CustomUser, OrganizationalUnit
from .test_util import set_up_user_with_interface_call_and_contract
from ..constants import CONTRACTEN


class DataModelTest(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self)

    def test_stage_contract(self):
        expected = 'StageContract: NL-123: Test contract naam'
        self.assertEqual(self.stage_contract_1.__str__(), expected)

    def testContractsOfInterfaceCall_one_contract(self):
        contracts = self.interface_call_1.stage_contracts()
        self.assertEqual(len(contracts), 1)

    def testContractsOfInterfaceCall_two_contracts(self):
        self.stage_contract_2 = StageContract.objects.create(contract_nr='NL-123',
                                                             seq_nr=0,
                                                             description='Test Contract 2',
                                                             contract_owner='T. Ester',
                                                             contract_name='Test contract naam',
                                                             data_per_org_unit=self.data_per_org_unit)

        contracts = self.interface_call_1.stage_contracts()
        self.assertEqual(len(contracts), 2)


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


class OrgUnitTests(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self)

    def test_get_org_unit_found_by_system(self):
        mapping_name = "my_map"
        mapping = Mapping.objects.create(name=mapping_name,
                                         system=self.system_a,
                                         org_unit=self.org_unit)
        found_org_unit = get_org_unit(self.system_a, mapping_name)
        self.assertEqual(self.org_unit.name, found_org_unit.name)

    def test_get_org_unit_found_by_system_name(self):
        mapping_name = "my_map"
        mapping = Mapping.objects.create(name=mapping_name,
                                         system=self.system_a,
                                         org_unit=self.org_unit)
        found_org_unit = get_org_unit(self.system_a.name, mapping_name)
        self.assertEqual(self.org_unit.name, found_org_unit.name)

    def test_get_org_unit_unknown_system_name(self):
        mapping_name = "my_map"
        mapping = Mapping.objects.create(name=mapping_name,
                                         system=self.system_a,
                                         org_unit=self.org_unit)
        found_org_unit = get_org_unit("SYSTEM UNKNOWN", mapping_name)
        self.assertIsNone(found_org_unit)

    def test_get_org_unit_unknown_mapping(self):
        not_existing_mapping_name = "Not existing"
        mapping_name = "my_map"
        mapping = Mapping.objects.create(name=mapping_name,
                                         system=self.system_a,
                                         org_unit=self.org_unit)
        found_org_unit = get_org_unit(self.system_a, not_existing_mapping_name)
        self.assertIsNone(found_org_unit)


class DoesUserBelongToOrgUnitTests(TestCase):

    def test_user_with_no_org(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        self.assertFalse(lonely_user.is_authorized_for_org_unit(a_team))

    def test_user_with_right_org_unit(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        lonely_user.org_units.add(a_team)
        self.assertTrue(lonely_user.is_authorized_for_org_unit(a_team))

    def test_user_with_other_org_unit(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        lonely_user.org_units.add(a_team)
        self.assertFalse(lonely_user.is_authorized_for_org_unit(b_team))

    def test_user_with_cluster_with_a_team(self):
        cluster_chef = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        a_cluster = OrganizationalUnit.objects.create(name="A-cluster", type=OrganizationalUnit.CLUSTER)
        a_team.parent_org_unit = a_cluster
        cluster_chef.org_units.add(a_cluster)
        self.assertTrue(cluster_chef.is_authorized_for_org_unit(a_cluster))
        self.assertTrue(cluster_chef.is_authorized_for_org_unit(a_team))

    def test_user_with_cluster_with_a_team(self):
        dep_chef = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        a_cluster = OrganizationalUnit.objects.create(name="A-cluster", type=OrganizationalUnit.CLUSTER)
        a_departement = OrganizationalUnit.objects.create(name="A-department", type=OrganizationalUnit.AFDELING)
        a_team.parent_org_unit = a_cluster
        a_cluster.parent_org_unit = a_departement
        dep_chef.org_units.add(a_departement)
        self.assertTrue(dep_chef.is_authorized_for_org_unit(a_departement))
        self.assertTrue(dep_chef.is_authorized_for_org_unit(a_cluster))
        self.assertTrue(dep_chef.is_authorized_for_org_unit(a_team))
        self.assertFalse(dep_chef.is_authorized_for_org_unit(b_team))

    def test_loop_beveiliging(self):
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        a_team.parent_org_unit = b_team
        b_team.parent_org_unit = a_team
        a_cluster = OrganizationalUnit.objects.create(name="A-cluster", type=OrganizationalUnit.CLUSTER)
        a_departement = OrganizationalUnit.objects.create(name="A-department", type=OrganizationalUnit.AFDELING)
        dep_chef = CustomUser.objects.create(username="Lonely")
        dep_chef.org_units.add(a_departement)
        with self.assertRaises(Exception):
            dep_chef.is_authorized_for_org_unit(a_team)

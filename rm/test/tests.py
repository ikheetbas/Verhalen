from django.db.models.functions import Now
from django.test import TestCase
from django.urls import reverse

from rm.interface_file import get_org_unit
from rm.models import Contract, Mapping, System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit

from django.db.utils import IntegrityError

from users.models import CustomUser, OrganizationalUnit
from .test_util import set_up_user_with_interface_call_and_contract
from ..constants import CONTRACTEN, NEGOMETRIX


class DataModelTest(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self)

    def test_contract(self):
        expected = 'NL-123: Test contract naam'
        self.assertEqual(self.contract_1.__str__(), expected)

    def testContractsOfInterfaceCall_one_contract(self):
        contracts = self.interface_call.contracts()
        self.assertEqual(len(contracts), 1)

    def testContractsOfInterfaceCall_two_contracts(self):
        self.contract_2 = Contract.objects.create(contract_nr='NL-123',
                                                  seq_nr=0,
                                                  description='Test Contract 2',
                                                  contract_owner='T. Ester',
                                                  contract_name='Test contract naam',
                                                  data_per_org_unit=self.data_per_org_unit)

        contracts = self.interface_call.contracts()
        self.assertEqual(len(contracts), 2)


class WebPagesTest(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self)

    def test_homepage(self):
        c = self.client
        response = c.get("/")
        self.assertEqual(response.status_code, 200)

    def test_one_interface_call_on_page(self):
        response = self.client.get('/interfacecalls')
        self.assertContains(response, 'TestStatus')

    def test_one_contract_on_interface_call_page(self):
        response = self.client.get(f'/interfacecall/{self.interface_call.pk}/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester')

    def test_two_contract_on_interface_call_page(self):
        Contract.objects.create(contract_nr='NL-345',
                                seq_nr=1,
                                description='Test Contract 2',
                                contract_owner='T. Ester',
                                data_per_org_unit=self.data_per_org_unit)
        response = self.client.get(f'/interfacecall/{self.interface_call.pk}/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=2)

        self.assertContains(response, 'NL-345')
        self.assertContains(response, 'Test Contract 2')

    def test_create_contract_without_parent(self):
        try:
            Contract.objects.create(seq_nr=0, contract_nr="NL-123", data_per_org_unit=self.data_per_org_unit)
        except IntegrityError as exception:
            expected = "null value in column \"interface_call_id\" " \
                       "violates not-null constraint"
            self.assertTrue(expected in exception.__str__())


class LoginRequiredTests(TestCase):
    """
    All pages require login, except the login page
    """

    def test_login_required_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse('account_login') + "?next=/")

    def test_login_required_upload_page(self):
        response = self.client.get(reverse("upload"))
        self.assertRedirects(response, reverse('account_login') + "?next=/upload/")


class RoleBasedAuthorizationSuperuserTests(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self, superuser=True)

    def test_superuser_sees_upload_button(self):
        response = self.client.get(reverse("interface_call_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload file')

    def test_superuser_can_access_upload_form(self):
        response = self.client.get(reverse("upload"))
        self.assertEqual(response.status_code, 200)

    def test_superuser_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interface_call.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=1)


class RoleBasedAuthorizationClusterLeadTests(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self, superuser=False, group_name="Cluster Lead")
        # print_permissions_and_groups()

    def test_cluster_lead_sees_no_upload_button(self):
        response = self.client.get(reverse("interface_call_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Upload file</a>')

    def test_cluster_lead_can_not_access_upload_form(self):
        response = self.client.get(reverse("upload"))
        self.assertEqual(response.status_code, 403)

    def test_cluster_lead_has_view_contract_permissions(self):
        permissions = self.user.user_permissions.all()
        self.assertTrue(self.user.has_perm('rm.view_contract'))

    def test_cluster_lead_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interface_call.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=1)


class RoleBasedAuthorizationBuyerTests(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self, superuser=False, group_name="Buyer")

    def test_buyer_sees_upload_button(self):
        response = self.client.get(reverse("interface_call_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload file')

    def test_buyer_can_access_upload_form(self):
        response = self.client.get(reverse("upload"))
        self.assertEqual(response.status_code, 200)

    def test_buyer_has_the_right_permissions(self):
        permissions = self.user.user_permissions.all()
        self.assertTrue(self.user.has_perm('rm.view_contract'))
        self.assertTrue(self.user.has_perm('rm.upload_contract_file'))
        self.assertTrue(self.user.has_perm('rm.call_contract_interface'))

    def test_buyer_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interface_call.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract 1')
        self.assertContains(response, 'T. Ester', count=1)


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


class DeactivationsTests(TestCase):

    def setUp(self):
        self.system, create = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.create(system=self.system,
                                                                       data_set_type=self.data_set_type,
                                                                       interface_type=InterfaceDefinition.UPLOAD)
        self.org_unit = OrganizationalUnit.objects.create(name="IAAS")

        self.interface_call = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                           date_time_creation=Now(),
                                                           status=InterfaceCall.ACTIVE)
        self.data_per_org_unit = DataPerOrgUnit.objects.create(interface_call=self.interface_call,
                                                               org_unit=self.org_unit,
                                                               active=True)
        self.contract_1 = Contract.objects.create(data_per_org_unit=self.data_per_org_unit, seq_nr=0)
        self.contract_2 = Contract.objects.create(data_per_org_unit=self.data_per_org_unit, seq_nr=1)

    def test_deactivate_data_per_org_unit_happy_path(self):
        self.assertEqual(self.data_per_org_unit.contract_set.all().count(), 2)

        self.data_per_org_unit.deactivate()
        self.assertEqual(self.data_per_org_unit.contract_set.all().count(), 0)

    def test_deactivate_data_per_org_unit_not_active(self):
        self.data_per_org_unit.active = False  # NOT NORMAL BEHAVIOR, JUST FOR TESTING
        self.assertEqual(self.data_per_org_unit.contract_set.all().count(), 2)

        with self.assertRaises(RuntimeError):
            self.data_per_org_unit.deactivate()

        self.assertEqual(self.data_per_org_unit.contract_set.all().count(), 2)

    def test_deactivate_interface_call_happy_path(self):
        self.assertEqual(self.interface_call.contracts().count(),2)
        self.interface_call.deactivate()
        self.assertEqual(self.interface_call.contracts().count(), 0)


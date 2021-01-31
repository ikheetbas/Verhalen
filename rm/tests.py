from django.test import TestCase
from django.urls import reverse

from .interface_file import get_org_unit
from .models import Contract, Mapping

from django.db.utils import IntegrityError
from .test_util import set_up_user_with_interface_call_and_contract


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

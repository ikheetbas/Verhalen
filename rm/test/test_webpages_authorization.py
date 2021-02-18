from django.test import TestCase
from django.urls import reverse

from rm.test import test_util


class RoleBasedAuthorizationSuperuserTests(TestCase):

    def setUp(self):
        test_util.set_up_user_login_with_interface_call_and_contract(self, superuser=True)

    def test_superuser_sees_upload_button(self):
        self.assertTrue(self.user.is_superuser)
        response = self.client.get(reverse("interface_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/contracten_upload/"')

    def test_superuser_can_access_upload_form(self):
        response = self.client.get(reverse("contracten_upload_details"))
        self.assertEqual(response.status_code, 200)

    def test_superuser_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interface_call_1.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=1)


class RoleBasedAuthorizationClusterLeadTests(TestCase):

    def setUp(self):
        test_util.set_up_user_login_with_interface_call_and_contract(self, superuser=False, group_name="Cluster Lead")
        # print_permissions_and_groups()

    def test_cluster_lead_sees_no_upload_button(self):
        response = self.client.get(reverse("uploads_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Upload file</a>')

    def test_cluster_lead_can_not_access_upload_form(self):
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 403)

    def test_cluster_lead_has_contracten_view_permissions(self):
        permissions = self.user.user_permissions.all()
        self.assertTrue(self.user.has_perm('rm.contracten_view'))

    def test_cluster_lead_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interface_call_1.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=1)


class RoleBasedAuthorizationBuyerTests(TestCase):

    def setUp(self):
        test_util.set_up_user_login_with_interface_call_and_contract(self, superuser=False, group_name="Buyer")

    def test_buyer_sees_upload_button(self):
        response = self.client.get(reverse("interface_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/contracten_upload/"')

    def test_buyer_can_access_upload_form(self):
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 200)


    def test_buyer_has_the_right_permissions(self):
        permissions = self.user.user_permissions.all()
        self.assertFalse(self.user.has_perm('rm.view_contract'))                # OLD
        self.assertFalse(self.user.has_perm('rm.upload_contract_file'))         # OLD
        self.assertTrue(self.user.has_perm('rm.contracten_api'))
        self.assertTrue(self.user.has_perm('rm.contracten_upload'))
        self.assertTrue(self.user.has_perm('rm.contracten_view'))

    def test_buyer_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/contracten_upload_details/{self.interface_call_1.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract 1')
        self.assertContains(response, 'T. Ester', count=1)
        self.assertContains(response, 'Activeer upload')
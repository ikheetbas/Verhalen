from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from rm.constants import CONTRACTEN
from rm.models import System, DataSetType, InterfaceDefinition
from rm.test.test_util import set_up_user_with_interface_call_and_contract, set_up_user
from stage.models import StageContract


def _create_superuser():
    user = get_user_model().objects.create(username="Admin",
                                           is_superuser=True,
                                           is_active=True)
    user.save()
    return user


def _create_user(username, group_name=None):
    user = get_user_model().objects.create(username=username,
                                           is_active=True)

    if group_name:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            message = f"Group {group_name} can not be found"
            raise Exception(message)
        user.groups.add(group)

    user.save()
    return user


class HomepageTest(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self)

    def test_homepage(self):
        c = self.client
        response = c.get("/")
        self.assertEqual(response.status_code, 200)


class InterfacesPageTest(TestCase):

    def setUp(self):
        self.system = System.objects.get(name="Negometrix")
        self.data_set_type = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.get(name="Contracten upload")

    def test_sanity(self):
        self.assertTrue(self.interface_definition.interface_type, InterfaceDefinition.UPLOAD)

    def test_interfaces_page_user_no_permissions_and_no_org_unit(self):
        set_up_user(self, superuser=False)

        # Must be able to load the page
        response = self.client.get('/interfaces')
        self.assertContains(response, 'Interfaces')

        # Must see the Contracten and Negometrix and Upload text
        self.assertContains(response, 'Contracten')
        self.assertContains(response, 'Negometrix')
        self.assertContains(response, 'Upload')

        # Should not see an upload link
        self.assertNotContains(response, 'Upload</a>')

    def test_interfaces_page_buyer(self):
        set_up_user(self, superuser=False, group_name="Buyer")

        # Must be able to load the page and see an Upload button
        response = self.client.get('/interfaces')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload</a>')

    def test_interfaces_page_superuser(self):
        set_up_user(self, superuser=True)

        # Must be able to load the page and see an Upload button
        response = self.client.get('/interfaces')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload</a>')


class ContractenUploadDetailsPageTest(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self)

    def test_one_contract_on_interface_call_page(self):
        response = self.client.get(f'/contracten_upload_details/{self.interface_call_1.pk}/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester')

    def test_two_contract_on_interface_call_page(self):
        StageContract.objects.create(contract_nr='NL-345',
                                     seq_nr=1,
                                     description='Test Contract 2',
                                     contract_owner='T. Ester',
                                     data_per_org_unit=self.data_per_org_unit)
        response = self.client.get(f'/interfacecall/{self.interface_call_1.pk}/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=2)

        self.assertContains(response, 'NL-345')
        self.assertContains(response, 'Test Contract 2')

    def test_create_contract_without_parent(self):
        try:
            StageContract.objects.create(seq_nr=0, contract_nr="NL-123", data_per_org_unit=self.data_per_org_unit)
        except IntegrityError as exception:
            expected = "null value in column \"interface_call_id\" " \
                       "violates not-null constraint"
            self.assertTrue(expected in exception.__str__())




class ContractenUploadPageTest(TestCase):

    def setUp(self):

        self.superuser = _create_superuser()
        self.user_buyer = _create_user(username="B.Inkoper", group_name="Buyer")
        self.user_no_role = _create_user(username="Bas")

    def _login_superuser(self):
        self.client.logout()
        self.client.force_login(self.superuser)

    def _login_user_buyer(self):
        self.client.logout()
        self.client.force_login(self.user_buyer)

    def _login_user_no_role(self):
        self.client.logout()
        self.client.force_login(self.user_no_role)

    def test_upload_page_with_admin(self):
        self._login_superuser()
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contracten Upload')

    def test_upload_page_with_buyer(self):
        self._login_user_buyer()
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contracten Upload')

    def test_upload_page_with_no_role(self):
        self._login_user_no_role()
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 403)




class LoginRequiredTests(TestCase):
    """
    All pages require login, except the login page
    """

    def test_login_required_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse('account_login') + "?next=/")

    def test_login_required_upload_page(self):
        response = self.client.get(reverse("contracten_upload"))
        self.assertRedirects(response, reverse('account_login') + "?next=/contracten_upload/")

    def test_inloggen_text(self):
        response = self.client.get(reverse("account_login"))
        self.assertContains(response, 'Inloggen')


class RoleBasedAuthorizationSuperuserTests(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self, superuser=True)

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
        set_up_user_with_interface_call_and_contract(self, superuser=False, group_name="Cluster Lead")
        # print_permissions_and_groups()

    def test_cluster_lead_sees_no_upload_button(self):
        response = self.client.get(reverse("uploads_list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Upload file</a>')

    def test_cluster_lead_can_not_access_upload_form(self):
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 403)

    def test_cluster_lead_has_view_contract_permissions(self):
        permissions = self.user.user_permissions.all()
        self.assertTrue(self.user.has_perm('rm.view_contract'))

    def test_cluster_lead_sees_contracts_of_interfaceCall(self):
        response = self.client.get(f'/interfacecall/{self.interface_call_1.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=1)


class RoleBasedAuthorizationBuyerTests(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self, superuser=False, group_name="Buyer")

    def test_buyer_sees_upload_button(self):
        response = self.client.get(reverse("interface_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/contracten_upload/"')

    def test_buyer_can_access_upload_form(self):
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 200)


    def test_buyer_has_the_right_permissions(self):
        permissions = self.user.user_permissions.all()
        self.assertTrue(self.user.has_perm('rm.view_contract'))
        self.assertTrue(self.user.has_perm('rm.upload_contract_file'))
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

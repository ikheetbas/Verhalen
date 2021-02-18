from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from rm.constants import CONTRACTEN
from rm.models import System, DataSetType, InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from rm.test import test_util
# from rm.test.test_util import set_up_user_login_with_interface_call_and_contract, set_up_user_and_login
from stage.models import StageContract
from users.models import OrganizationalUnit, CustomUser


def _create_superuser():
    """
    Create a superuser, no login etc
    """
    user = get_user_model().objects.create(username="Admin",
                                           is_superuser=True,
                                           is_active=True)
    user.save()
    return user


def _create_user(username, group_name=None):
    """
    Create user with optional a group
    """
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


class InterfacesPageTest(TestCase):

    def setUp(self):
        self.system = System.objects.get(name="Negometrix")
        self.data_set_type = DataSetType.objects.get_or_create(name=CONTRACTEN)
        self.interface_definition = InterfaceDefinition.objects.get(name="Contracten upload")

    def test_sanity(self):
        self.assertTrue(self.interface_definition.interface_type, InterfaceDefinition.UPLOAD)

    def test_interfaces_page_user_no_permissions_and_no_org_unit(self):
        test_util.set_up_user_and_login(self, superuser=False)

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
        test_util.set_up_user_and_login(self, superuser=False, group_name="Buyer")

        # Must be able to load the page and see an Upload button
        response = self.client.get('/interfaces')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload</a>')

    def test_interfaces_page_superuser(self):
        test_util.set_up_user_and_login(self, superuser=True)

        # Must be able to load the page and see an Upload button
        response = self.client.get('/interfaces')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload</a>')


class ContractenUploadPageTestAccess(TestCase):

    def setUp(self):
        self.superuser = test_util.create_superuser()
        self.user_buyer = test_util.create_user(username="B.Inkoper", group_name="Buyer")
        self.cluster_lead = test_util.create_user(username="Bart", group_name="Cluster Lead")
        self.user_no_role = test_util.create_user(username="Bas")

    def _login_user(self, user):
        test_util.login_user(self.client, user)

    def test_upload_page_with_admin(self):
        self._login_user(self.superuser)

        # Can access Contract Upload page
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contracten Upload')

        # Can browse for file and submit
        self.assertContains(response, '<input type="file"')
        self.assertContains(response, "Submit")

    def test_upload_page_with_buyer(self):
        self._login_user(self.user_buyer)

        # Can access Contract Upload page
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contracten Upload')

        # Can browse for file and submit
        self.assertContains(response, '<input type="file"')
        self.assertContains(response, "Submit")

    def test_upload_page_cluster_lead(self):
        self._login_user(self.cluster_lead)

        # Can NOT access Contract Upload page
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 403)

    def test_upload_page_with_no_role(self):
        self._login_user(self.user_no_role)

        # Can NOT access Contract Upload page
        response = self.client.get(reverse("contracten_upload"))
        self.assertEqual(response.status_code, 403)


class ContractenUploadPageSeeResultUpload(TestCase):

    def setUp(self):
        self.superuser = test_util.create_superuser()

        self.user_buyer_iaas: CustomUser = test_util.create_user(username="InkoperIaaS", group_name="Buyer")
        self.iaas = OrganizationalUnit.objects.get(name="PT: IaaS")
        self.user_buyer_iaas.org_units.add(self.iaas)

        self.user_buyer_hosting = test_util.create_user(username="InkoperHosting", group_name="Buyer")
        # self.hosting = OrganizationalUnit.objects.get(name="PT: Hosting & Streaming")
        # self.user_buyer_hosting.org_units.add(self.hosting)

        self.cluster_lead_iaas = test_util.create_user(username="Bart", group_name="Cluster Lead")
        self.cluster_lead_iaas.org_units.add(self.iaas)

        self.user_no_role = test_util.create_user(username="Bas")

        pt_iaas = OrganizationalUnit.objects.get(name="PT: IaaS")
        interface_def = InterfaceDefinition.objects.get(name="Contracten upload")
        self.upload_iaas = InterfaceCall.objects.create(interface_definition=interface_def,
                                                        status=InterfaceCall.OK,
                                                        )
        self.dpou = DataPerOrgUnit.objects.create(interface_call=self.upload_iaas,
                                                  org_unit=pt_iaas)
        stage_contract = StageContract.objects.create(data_per_org_unit=self.dpou,
                                                      seq_nr=1,
                                                      contract_nr=123,
                                                      contract_name="Schoonmaak",
                                                      contract_status="SCHOON")

    def _login_user(self, user):
        test_util.login_user(self.client, user)

    def test_upload_page_with_admin(self):
        self._login_user(self.superuser)
        self._can_see_all()

    def test_upload_page_with_buyer_iaas(self):
        self._login_user(self.user_buyer_iaas)
        self._can_see_all()

    def test_upload_page_with_buyer_hosting_FORBIDDEN(self):
        self._login_user(self.user_buyer_hosting)
        response = self.client.get(reverse("contracten_upload", args=(self.upload_iaas.id,)))

        # Should NOT see the page, since it is for another org unit
        self.assertEqual(response.status_code, 403)

    def test_upload_page_with_cluster_lead_iaas(self):
        self._login_user(self.cluster_lead_iaas)
        response = self.client.get(reverse("contracten_upload", args=(self.upload_iaas.id,)))

        # Should NOT see the page, since Cluster Leas are not allowed to upload
        self.assertEqual(response.status_code, 403)

    def _can_see_all(self):
        # Can access Contract Upload page
        response = self.client.get(reverse("contracten_upload", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contracten Upload')

        # Can browse for file and submit
        self.assertContains(response, '<input type="file"')
        self.assertContains(response, "Submit")

        # Can see Activate button and see that it was a Negometrix file with a contract for IaaS
        self.assertContains(response, 'value="Activeer upload"')
        self.assertContains(response, "Negometrix")
        self.assertContains(response, "Contracten PT: IaaS")
        self.assertContains(response, "Schoonmaak")

    def _can_see_but_not_activate(self):
        # Can access Contract Upload page
        response = self.client.get(reverse("contracten_upload", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contracten Upload')

        # Can browse for file and submit
        self.assertNotContains(response, '<input type="file"')
        self.assertNotContains(response, "Submit")

        # Can see Activate button and see that it was a Negometrix file with a contract for IaaS
        self.assertNotContains(response, 'value="Activeer upload_iaas"')
        self.assertContains(response, "Negometrix")
        self.assertContains(response, "Contracten PT: xIaaS")
        self.assertContains(response, "Schoonmaak")



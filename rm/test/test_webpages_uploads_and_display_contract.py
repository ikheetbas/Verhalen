from django.test import TestCase
from django.urls import reverse

from rm.models import InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from rm.test import test_util
from stage.models import StageContract
from users.admin import CustomUser
from users.models import OrganizationalUnit


class UploadsPageTest(TestCase):

    def setUp(self):
        # Superuser
        self.superuser = test_util.create_superuser()

        # Buyer IAAS
        self.user_buyer_iaas: CustomUser = test_util.create_user(username="InkoperIaaS", group_name="Buyer")
        self.iaas = OrganizationalUnit.objects.get(name="PT: IaaS")
        self.user_buyer_iaas.org_units.add(self.iaas)

        # Buyer Hosting
        self.user_buyer_hosting = test_util.create_user(username="InkoperHosting", group_name="Buyer")
        self.hosting = OrganizationalUnit.objects.get(name="PT: Hosting & Streaming")
        self.user_buyer_hosting.org_units.add(self.hosting)

        # Cluster lead IAAS
        self.cluster_lead_iaas = test_util.create_user(username="Bart", group_name="Cluster Lead")
        self.cluster_lead_iaas.org_units.add(self.iaas)

        # User with nothing
        self.user_no_role_no_org = test_util.create_user(username="Bas")

        # Interface call for iaas
        interface_def = InterfaceDefinition.objects.get(name="Contracten upload")
        self.upload_iaas = InterfaceCall.objects.create(interface_definition=interface_def,
                                                        status=InterfaceCall.ACTIVE,
                                                        )
        self.dpou_iaas = DataPerOrgUnit.objects.create(interface_call=self.upload_iaas,
                                                       org_unit=self.iaas)
        StageContract.objects.create(data_per_org_unit=self.dpou_iaas,
                                     seq_nr=1,
                                     contract_nr=123,
                                     contract_name="Schoonmaak",
                                     contract_status="SCHOON")

        # Interface call for hosting
        interface_def = InterfaceDefinition.objects.get(name="Contracten upload")
        self.upload_hosting = InterfaceCall.objects.create(interface_definition=interface_def,
                                                           status=InterfaceCall.OK,
                                                           )
        self.dpou_hosting = DataPerOrgUnit.objects.create(interface_call=self.upload_hosting,
                                                          org_unit=self.hosting)
        StageContract.objects.create(data_per_org_unit=self.dpou_hosting,
                                     seq_nr=1,
                                     contract_nr=234,
                                     contract_name="Schoonmaak",
                                     contract_status="SCHOON")

        # Interface call for hosting & iaas
        interface_def = InterfaceDefinition.objects.get(name="Contracten upload")
        self.upload_hosting_and_iaas = InterfaceCall.objects.create(interface_definition=interface_def,
                                                                    status=InterfaceCall.OK,
                                                                    )
        self.dpou_hosting_2 = DataPerOrgUnit.objects.create(interface_call=self.upload_hosting_and_iaas,
                                                            org_unit=self.hosting)
        StageContract.objects.create(data_per_org_unit=self.dpou_hosting_2,
                                     seq_nr=1,
                                     contract_nr=345,
                                     contract_name="Schoonmaak",
                                     contract_status="SCHOON")

        self.dpou_iaas_2 = DataPerOrgUnit.objects.create(interface_call=self.upload_hosting_and_iaas,
                                                            org_unit=self.iaas)
        StageContract.objects.create(data_per_org_unit=self.dpou_iaas_2,
                                     seq_nr=1,
                                     contract_nr=456,
                                     contract_name="Schoonmaak",
                                     contract_status="SCHOON")

    def _login_user(self, user):
        test_util.login_user(self.client, user)

    def test_everybody_can_see_upload_in_menu(self):
        self._login_user(self.user_no_role_no_org)

        # Can access homepage with menu entry uploads
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a class="nav-link" href="/uploads">')

    def test_everybody_can_see_uploads_page(self):
        self._login_user(self.user_no_role_no_org)

        # Can access page with uploads
        response = self.client.get(reverse("uploads_list"))
        self.assertEqual(response.status_code, 200)

        # Can see the upload
        self.assertContains(response, 'Contracten')
        self.assertContains(response, 'Negometrix')
        self.assertContains(response, 'Upload')
        self.assertContains(response, 'ACTIVE')

    def test_buyer_can_see_upload_in_menu(self):
        self._login_user(self.user_buyer_iaas)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a class="nav-link" href="/uploads">')

    def test_buyer_iaas_can_see_uploads_page_and_click_to_the_iaas_details_page(self):
        self._login_user(self.user_buyer_iaas)

        # Can access page with uploads
        response = self.client.get(reverse("uploads_list"))
        self.assertEqual(response.status_code, 200)

        # Can see the upload
        self.assertContains(response, '<td>Contracten</td>', 3)
        self.assertContains(response, '<td>Negometrix</td>', 3)
        self.assertContains(response, 'ACTIVE', 1)
        self.assertContains(response, 'OK', 2)

        # Can click the iaas upload
        self.assertContains(response, f"<a href='/contracten_upload_details/{self.upload_iaas.id}")

        # Can not click the hosting uploads
        self.assertNotContains(response, f"<a href='/contracten_upload_details/{self.upload_hosting.id}")
        self.assertNotContains(response, f"<a href='/contracten_upload_details/{self.upload_hosting_and_iaas.id}")

    def test_buyer_hosting_can_see_uploads_page_and_click_to_the_hosting_details_page(self):
        self._login_user(self.user_buyer_hosting)

        # Can access page with uploads
        response = self.client.get(reverse("uploads_list"))
        self.assertEqual(response.status_code, 200)

        # Can see the upload
        self.assertContains(response, '<td>Contracten</td>', 3)
        self.assertContains(response, '<td>Negometrix</td>', 3)
        self.assertContains(response, 'ACTIVE', 1)
        self.assertContains(response, 'OK', 2)

        # Can NOT click the iaas upload
        self.assertNotContains(response, f"<a href='/contracten_upload_details/{self.upload_iaas.id}")
        self.assertNotContains(response, f"<a href='/contracten_upload_details/{self.upload_hosting_and_iaas.id}")

        # Can click the hosting uploads
        self.assertContains(response, f"<a href='/contracten_upload_details/{self.upload_hosting.id}")

    def test_cluster_lead_iaas_can_see_uploads_page_and_click_to_the_details_page(self):
        self._login_user(self.cluster_lead_iaas)

        # Can access page with uploads
        response = self.client.get(reverse("uploads_list"))
        self.assertEqual(response.status_code, 200)

        # Can see the upload
        self.assertContains(response, '<td>Contracten</td>', 3)
        self.assertContains(response, '<td>Negometrix</td>', 3)
        self.assertContains(response, 'ACTIVE', 1)
        self.assertContains(response, 'OK', 2)

        # Can click the iaas upload
        self.assertContains(response, f"<a href='/contracten_upload_details/{self.upload_iaas.id}")

        # Can not click the hosting uploads
        self.assertNotContains(response, f"<a href='/contracten_upload_details/{self.upload_hosting.id}")
        self.assertNotContains(response, f"<a href='/contracten_upload_details/{self.upload_hosting_and_iaas.id}")


class ContractenUploadDetailsPageTest(TestCase):

    def setUp(self):

        # Buyer Hosting
        self.user_buyer_hosting = test_util.create_user(username="InkoperHosting", group_name="Buyer")
        self.hosting = OrganizationalUnit.objects.get(name="PT: Hosting & Streaming")
        self.user_buyer_hosting.org_units.add(self.hosting)

        # Buyer IAAS
        self.user_buyer_iaas: CustomUser = test_util.create_user(username="InkoperIaaS", group_name="Buyer")
        self.iaas = OrganizationalUnit.objects.get(name="PT: IaaS")
        self.user_buyer_iaas.org_units.add(self.iaas)

        # Cluster lead IAAS
        self.cluster_lead_iaas = test_util.create_user(username="Bart", group_name="Cluster Lead")
        self.cluster_lead_iaas.org_units.add(self.iaas)

        # User with nothing from IaaS, no permissions
        self.user_iaas_no_role = test_util.create_user(username="Bas")
        self.user_iaas_no_role.org_units.add(self.iaas)

        # Interface call for iaas
        interface_def = InterfaceDefinition.objects.get(name="Contracten upload")
        self.upload_iaas = InterfaceCall.objects.create(interface_definition=interface_def,
                                                        status=InterfaceCall.INACTIVE,
                                                        )
        self.dpou_iaas = DataPerOrgUnit.objects.create(interface_call=self.upload_iaas,
                                                       org_unit=self.iaas,
                                                       active=False)

        StageContract.objects.create(data_per_org_unit=self.dpou_iaas,
                                     seq_nr=1,
                                     contract_nr=123,
                                     contract_name="Schoonmaak",
                                     contract_status="SCHOON")

    def _login_user(self, user):
        test_util.login_user(self.client, user)

    def test_user_from_wrong_org_unit_cannot_access(self):
        # Buyer from Hosting
        self._login_user(self.user_buyer_hosting)

        # Should NOT be able to see page with IaaS contracts
        response = self.client.get(reverse("contracten_upload_details", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 403)

    def test_user_with_wrong_permission_cannot_access(self):
        # Iaas user without permissions
        self._login_user(self.user_iaas_no_role)

        # Should NOT be able to see page with IaaS contracts
        response = self.client.get(reverse("contracten_upload_details", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 403)

    def test_user_with_view_contract_permission_and_org_unit_can_access(self):
        # Cluster lead from IaaS
        self._login_user(self.cluster_lead_iaas)

        # Should be able to see page with IaaS contracts
        response = self.client.get(reverse("contracten_upload_details", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 200)

        # Should NOT see the Activate Button
        self.assertNotContains(response, "Activeer upload")
        self.assertContains(response, "Negometrix")

    def test_user_with_upload_contract_permission_and_org_unit_can_access_and_activate(self):
        # Buyer from IaaS
        self._login_user(self.user_buyer_iaas)

        # Should be able to see page with IaaS contracts
        response = self.client.get(reverse("contracten_upload_details", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 200)

        # Should see the Activate Button and see it is a Negometrix file
        self.assertContains(response, "INACTIVE")
        self.assertContains(response, "Activeer upload")
        self.assertContains(response, "Negometrix")

        # Press the Activate button
        response = self.client.post("/contracten_upload_details/",
                                    {"interface_call_id": self.upload_iaas.id,
                                     "activate": "Activeer upload"}, follow=True)
        self.assertContains(response, "ACTIVE")
        self.assertContains(response, "Deactiveer upload")
        self.assertContains(response, "Negometrix")
        self.assertContains(response, "Contracten PT: IaaS (Actief)")

        # Should see the Deactivate Button
        self.assertContains(response, "Deactiveer upload")

        # Press the Deactivate button
        response = self.client.post("/contracten_upload_details/",
                                    {"interface_call_id": self.upload_iaas.id,
                                     "deactivate": "Deactiveer upload"}, follow=True)
        self.assertContains(response, "INACTIVE")
        self.assertContains(response, "Activeer upload")
        self.assertContains(response, "Contracten PT: IaaS (Inactief)")



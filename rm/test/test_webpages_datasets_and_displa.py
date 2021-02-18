from django.test import TestCase
from django.urls import reverse

from rm.models import InterfaceDefinition, InterfaceCall, DataPerOrgUnit
from rm.test import test_util
from stage.models import StageContract
from users.models import CustomUser, OrganizationalUnit


class DatasetPageTest(TestCase):

    def setUp(self):

        # User with nothing
        self.user_no_role_no_org = test_util.create_user(username="Bas")

        # Buyer IAAS
        self.user_buyer_iaas: CustomUser = test_util.create_user(username="InkoperIaaS", group_name="Buyer")
        self.iaas = OrganizationalUnit.objects.get(name="PT: IaaS")
        self.user_buyer_iaas.org_units.add(self.iaas)

        # Cluster lead IAAS
        self.cluster_lead_iaas = test_util.create_user(username="Bart", group_name="Cluster Lead")
        self.cluster_lead_iaas.org_units.add(self.iaas)

        # Interface call for iaas
        interface_def = InterfaceDefinition.objects.get(name="Contracten upload")
        self.upload_iaas = InterfaceCall.objects.create(interface_definition=interface_def,
                                                        status=InterfaceCall.ACTIVE,
                                                        )
        self.dpou_iaas = DataPerOrgUnit.objects.create(interface_call=self.upload_iaas,
                                                       org_unit=self.iaas,
                                                       active=True)

        StageContract.objects.create(data_per_org_unit=self.dpou_iaas,
                                     seq_nr=1,
                                     contract_nr=123,
                                     contract_name="Schoonmaak",
                                     contract_status="SCHOON")


    def _login_user(self, user):
        test_util.login_user(self.client, user)

    def test_everybody_can_see_upload_in_menu(self):
        self._login_user(self.user_no_role_no_org)

        # Can access homepage with menu entry Datasets
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a class="nav-link" href="/datasets/">')

    def test_user_no_role_no_org_can_see_datasets_page_but_no_datasets(self):
        self._login_user(self.user_no_role_no_org)

        # Can access page with uploads
        response = self.client.get(reverse("dataset_list"))
        self.assertEqual(response.status_code, 200)

        # Can see no uploads, since it has no org units
        self.assertNotContains(response, 'Negometrix')
        self.assertNotContains(response, '<td class="actief-upload-status">Actief</td>')

    def test_user_with_wrong_permission_cannot_access(self):
        # user without permissions and orgs
        self._login_user(self.user_no_role_no_org)

        # Should NOT be able to see page with IaaS contracts
        response = self.client.get(reverse("contracten_dataset_details", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 403)


    def test_iaas_clusterlead_can_see_datasets_page_with_dataset_and_link(self):
        self._login_user(self.cluster_lead_iaas)

        # Can access page with uploads
        response = self.client.get(reverse("dataset_list"))
        self.assertEqual(response.status_code, 200)

        # Can see no uploads, since it has no org units
        self.assertContains(response, 'Negometrix')
        self.assertContains(response, '<td class="actief-upload-status">Actief</td>')
        self.assertContains(response, f'a href="/contracten_dataset_details/{self.upload_iaas.id}">{self.upload_iaas.id}</a>')

    def test_iaas_clusterlead_can_see_dataset_details_but_no_action_buttons(self):
        # Cluster lead from IaaS
        self._login_user(self.cluster_lead_iaas)

        # Should be able to see page with IaaS contracts
        response = self.client.get(reverse("contracten_dataset_details", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 200)

        # Should NOT see the Activate Button
        self.assertNotContains(response, "Activeer dataset")
        self.assertNotContains(response, "De-activeer dataset")
        self.assertContains(response, "Negometrix")
        self.assertContains(response, "Actief")

    def test_iaas_buyer_can_see_datasets_page_with_dataset_and_link(self):
        self._login_user(self.user_buyer_iaas)

        # Can access page with uploads
        response = self.client.get(reverse("dataset_list"))
        self.assertEqual(response.status_code, 200)

        # Can see no uploads, since it has no org units
        self.assertContains(response, 'Negometrix')
        self.assertContains(response, '<td class="actief-upload-status">Actief</td>')
        self.assertContains(response, f'a href="/contracten_dataset_details/{self.upload_iaas.id}">{self.upload_iaas.id}</a>')

    def test_iaas_buyer_can_see_dataset_details_with_action_buttons(self):
        # Cluster lead from IaaS
        self._login_user(self.user_buyer_iaas)

        # Should be able to see page with IaaS contracts
        response = self.client.get(reverse("contracten_dataset_details", args=(self.upload_iaas.id,)))
        self.assertEqual(response.status_code, 200)

        # Should NOT see the Activate Button
        self.assertNotContains(response, "Activeer dataset")
        self.assertContains(response, "De-activeer dataset")
        self.assertContains(response, "Negometrix")
        self.assertContains(response, "Actief")

        # Press the Deactivate button
        response = self.client.post("/contracten_dataset_details/",
                                    {"dpou_id": self.dpou_iaas.id,
                                     "deactivate": "De-activeer dataset"}, follow=True)
        self.assertContains(response, "Inactief")
        self.assertContains(response, "Activeer dataset")
        self.assertContains(response, "PT: IaaS")

        # Press the Activate button
        response = self.client.post("/contracten_dataset_details/",
                                    {"dpou_id": self.dpou_iaas.id,
                                     "activate": "Activeer dataset"}, follow=True)
        self.assertContains(response, "Actief")
        self.assertContains(response, "De-activeer dataset")
        self.assertContains(response, "PT: IaaS")

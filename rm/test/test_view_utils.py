from unittest.mock import patch, Mock

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rm import view_util
from rm.constants import NEGOMETRIX, CONTRACTEN, URL_NAME_CONTRACTEN_UPLOAD
from rm.models import System, DataSetType, InterfaceDefinition, DataPerOrgUnit, InterfaceCall
from rm.test.test_util import set_up_user_and_login
from rm.view_util import create_addition_dataset_filter, get_datasets_for_user, \
    get_active_datasets_per_interface_for_users_org_units, InterfaceListRecord, process_file
from users.models import CustomUser
from users.models import OrganizationalUnit


class CreateAdditionalDatasetFilterActive(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(username="TestUser1")

    def test_create_addition_dataset_filter_active(self):
        params = {'active': 'TRUE'}
        expected_filter = {'active': 'True'}

        result_filter = create_addition_dataset_filter(self.user, params)
        self.assertEqual(result_filter, expected_filter)

    def test_create_addition_dataset_filter_inactive(self):
        params = {'active': 'False'}
        expected_filter = {'active': 'False'}

        result_filter = create_addition_dataset_filter(self.user, params)
        self.assertEqual(result_filter, expected_filter)

    def test_create_addition_dataset_filter_active_WRONG(self):
        params = {'active': 'WRONG'}
        expected_filter = {}

        result_filter = create_addition_dataset_filter(self.user, params)
        self.assertEqual(result_filter, expected_filter)


class CreateAdditionalDatasetFilterSystem(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create(username="TestUser1")
        self.system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        self.dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]

    def test_create_addition_dataset_filter_negometrix(self):
        params = {'dataset_type_contracten': 'Contracten'}
        expected_filter = {'interface_call__interface_definition__data_set_type_id=': self.dataset_type_contracten.id}

        result_filter = create_addition_dataset_filter(self.user, params)
        self.assertEqual(result_filter, expected_filter)

    def test_create_addition_dataset_filter_unknown_system(self):
        params = {'system': 'Unknown'}
        expected_filter = {}

        result_filter = create_addition_dataset_filter(self.user, params)
        self.assertEqual(result_filter, expected_filter)


class CreateAdditionalDatasetFilterResponsibility(TestCase):

    def setUp(self):
        content_type_interface_call = ContentType.objects.get_for_model(InterfaceCall)
        permission_contracten_upload = Permission.objects.get_or_create(codename="contracten_upload",
                                                                        name="Contracten upload",
                                                                        content_type=content_type_interface_call)
        self.user = CustomUser.objects.create(username="TestUser1")
        self.user_without_permissions = CustomUser.objects.create(username="no_permission_user")
        self.user.user_permissions.add(permission_contracten_upload[0])
        self.system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]

    def test_create_addition_dataset_filter_responsibility_user(self):
        params = {'my_datasets': 'True'}
        user_responsible_interface_names = ['Contracten upload', ]
        expected_filter = {'interface_call__interface_definition__name__in': user_responsible_interface_names}

        result_filter = create_addition_dataset_filter(self.user, params)
        self.assertEqual(result_filter, expected_filter)

    def test_create_addition_dataset_filter_responsibility_no_permissions(self):
        params = {'my_datasets': 'True'}
        user_responsible_interface_names = []
        expected_filter = {'interface_call__interface_definition__name__in': user_responsible_interface_names}

        result_filter = create_addition_dataset_filter(self.user_without_permissions, params)
        self.assertEqual(result_filter, expected_filter)


class ViewUtilTests(TestCase):

    def setUp(self):
        self.content_type_interface_call = ContentType.objects.get_for_model(InterfaceCall)
        permission_contracten_upload = Permission.objects.get_or_create(name="Contracten upload")
        self.user = CustomUser.objects.create(username="TestUser1")
        self.user.user_permissions.add(permission_contracten_upload[0])

        # STATICS: System, DatasetType
        self.system_negometrix, created = System.objects.get_or_create(name=NEGOMETRIX)
        self.data_set_type, created = DataSetType.objects.get_or_create(name=CONTRACTEN)

    def test_get_datasets_for_user_on_org_authorization(self):
        # Interface Definition
        self.interface_definition, created = \
            InterfaceDefinition.objects.get_or_create(system=self.system_negometrix,
                                                      data_set_type=self.data_set_type,
                                                      interface_type=InterfaceDefinition.UPLOAD)

        # ADMIN: User, Organization
        self.org_unit_1 = OrganizationalUnit.objects.create(name="Cluster1")
        self.org_unit_2 = OrganizationalUnit.objects.create(name="Cluster2")
        self.org_unit_3 = OrganizationalUnit.objects.create(name="Cluster3")
        self.org_unit_t1 = OrganizationalUnit.objects.create(name="Team1",
                                                             parent_org_unit=self.org_unit_1)

        self.user.org_units.add(self.org_unit_1)

        # PROCESS DATA: Interface Call and dpou_1
        self.interface_call = InterfaceCall.objects.create(interface_definition=self.interface_definition,
                                                           user=self.user,
                                                           status=InterfaceCall.ACTIVE)

        self.dpou_1 = DataPerOrgUnit.objects.create(org_unit=self.org_unit_1,
                                                    interface_call=self.interface_call,
                                                    active=True)

        # ACTION: get datasets visible for this user
        datasets = get_datasets_for_user(self.user, {})

        # POST: only 1, the dpou_1 we just created
        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0].id, self.dpou_1.id)

        # PRE-ACTION: add another dpou_1 to the interface call, with another cluster
        self.dpou_2 = DataPerOrgUnit.objects.create(org_unit=self.org_unit_2,
                                                    interface_call=self.interface_call,
                                                    active=True)

        # ACTION: get datasets visible for this user again
        datasets = get_datasets_for_user(self.user, {})

        # POST: only 1, the dpou_1 we just created (still)
        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0].id, self.dpou_1.id)

        # PRE-ACTION: add another INACTIVE dpou_1 to the interface call, with same cluster
        self.user.org_units.add(self.org_unit_3)
        self.dpou_3 = DataPerOrgUnit.objects.create(org_unit=self.org_unit_3,
                                                    interface_call=self.interface_call,
                                                    active=False)

        # ACTION: get datasets visible for this user again
        datasets = get_datasets_for_user(self.user, {'active': 'All'})

        # POST: now 2:
        self.assertEqual(len(datasets), 2)
        self.assertIn(self.dpou_1, datasets)
        self.assertIn(self.dpou_3, datasets)

        # PRE-ACTION: add another dpou, for the team (under cluster1, so visible)
        self.dpou_4 = DataPerOrgUnit.objects.create(org_unit=self.org_unit_t1,
                                                    interface_call=self.interface_call,
                                                    active=True)

        # ACTION: get datasets visible for this user again
        datasets = get_datasets_for_user(self.user, {'active': 'All'})

        # POST: now 3:
        self.assertEqual(len(datasets), 3)
        self.assertIn(self.dpou_1, datasets)
        self.assertIn(self.dpou_3, datasets)
        self.assertIn(self.dpou_4, datasets)

        # ACTION: get datasets visible for this user ACTIVE
        datasets = get_datasets_for_user(self.user, {'active': 'True'})

        # POST: now 2:
        self.assertEqual(len(datasets), 2)
        self.assertIn(self.dpou_1, datasets)
        # self.assertEqual(datasets[1].id, self.dpou_3.id)
        self.assertIn(self.dpou_4, datasets)

        # ACTION: get datasets visible for this user INACTIVE
        datasets = get_datasets_for_user(self.user, {'active': 'False'})

        # POST: now 1:
        self.assertEqual(len(datasets), 1)
        # self.assertEqual(datasets[0].id, self.dpou_1.id)
        self.assertEqual(datasets[0].id, self.dpou_3.id)
        # self.assertEqual(datasets[1].id, self.dpou_4.id)

    def test_get_datasets_filter_on_responsibility(self):
        self.org_unit_cluster1 = OrganizationalUnit.objects.create(name="Cluster1")
        self.user.org_units.add(self.org_unit_cluster1)

        # Interface Definition for Contracten upload & Contracten API
        self.int_def_contracten_upload = InterfaceDefinition.objects.get(name="Contracten upload")

        self.int_def_contracten_api = InterfaceDefinition.objects.create(name="Contracten API",
                                                                         system=self.system_negometrix,
                                                                         data_set_type=self.data_set_type,
                                                                         interface_type=InterfaceDefinition.API)

        self.int_call_contracten_upload = InterfaceCall.objects.create(
            interface_definition=self.int_def_contracten_upload,
            user=self.user,
            status=InterfaceCall.ACTIVE)

        self.int_call_contracten_api = InterfaceCall.objects.create(interface_definition=self.int_def_contracten_api,
                                                                    user=self.user,
                                                                    status=InterfaceCall.ACTIVE)

        # Define DPOU's for each Int_call
        self.dpou_contracten_upload = DataPerOrgUnit.objects.create(org_unit=self.org_unit_cluster1,
                                                                    interface_call=self.int_call_contracten_upload,
                                                                    active=True)

        self.dpou_contracten_api = DataPerOrgUnit.objects.create(org_unit=self.org_unit_cluster1,
                                                                 interface_call=self.int_call_contracten_api,
                                                                 active=True)

        # Test System for uploading Tests
        self.system_a_test = System.objects.create(name="Test System")
        self.data_set_type_a_test = DataSetType.objects.create(name="Tests")

        # Interface Definition for Testen upload & API
        self.int_def_testen_upload = InterfaceDefinition.objects.create(name="Testen upload",
                                                                        system=self.system_a_test,
                                                                        data_set_type=self.data_set_type_a_test,
                                                                        interface_type=InterfaceDefinition.UPLOAD)

        self.int_def_testen_api = InterfaceDefinition.objects.create(name="Testen API",
                                                                     system=self.system_a_test,
                                                                     data_set_type=self.data_set_type_a_test,
                                                                     interface_type=InterfaceDefinition.API)

        # Interface Calls for Testen upload & API
        self.int_call_testen_upload = InterfaceCall.objects.create(
            interface_definition=self.int_def_testen_upload,
            user=self.user,
            status=InterfaceCall.ACTIVE)

        self.int_call_testen_api = InterfaceCall.objects.create(
            interface_definition=self.int_def_testen_api,
            user=self.user,
            status=InterfaceCall.ACTIVE)

        # Define DPOU's for each Int_call
        self.dpou_testen_upload = DataPerOrgUnit.objects.create(org_unit=self.org_unit_cluster1,
                                                                interface_call=self.int_call_testen_upload,
                                                                active=True)

        self.dpou_testen_api = DataPerOrgUnit.objects.create(org_unit=self.org_unit_cluster1,
                                                             interface_call=self.int_call_testen_api,
                                                             active=True)

        # Just checking to see if all is good
        datasets = get_datasets_for_user(self.user, {'active': 'True'})
        self.assertEqual(len(datasets), 4)
        self.assertEqual(datasets[0].id, self.dpou_contracten_upload.id)
        self.assertEqual(datasets[1].id, self.dpou_contracten_api.id)
        self.assertEqual(datasets[2].id, self.dpou_testen_upload.id)
        self.assertEqual(datasets[3].id, self.dpou_testen_api.id)

        # Retrieve the datasets for which the user is responsible:
        # - only the Contracten upload, considering the users permissions
        datasets = get_datasets_for_user(self.user, {'my_datasets': 'True'})
        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0].id, self.dpou_contracten_upload.id)

        # add a permission for Contract API:
        permission_contracten_api = Permission.objects.get_or_create(codename="contracten_api",
                                                                     name="Contracten API",
                                                                     content_type=self.content_type_interface_call)[0]
        self.user.user_permissions.add(permission_contracten_api)

        # Permissions are cached, so using them directly after creation might fail (and it did!)
        # Be aware that user.refresh_from_db() won't clear the cache.
        self.user = get_object_or_404(CustomUser, pk=self.user.id)

        # now the user should see 2 datasets, one for the Contracten Upload, and 1 for the Contracten API
        datasets = get_datasets_for_user(self.user, {'my_datasets': 'True'})
        self.assertEqual(len(datasets), 2)
        self.assertEqual(datasets[0].id, self.dpou_contracten_upload.id)
        self.assertEqual(datasets[1].id, self.dpou_contracten_api.id)

        # Now test if we can use the filters mixed: responsibility and active
        self.dpou_contracten_upload.active = False
        self.dpou_contracten_upload.save()

        datasets = get_datasets_for_user(self.user, {'my_datasets': 'True', 'active': 'All'})
        self.assertEqual(len(datasets), 2)
        self.assertIn(self.dpou_contracten_upload, datasets)
        self.assertIn(self.dpou_contracten_api, datasets)

        datasets = get_datasets_for_user(self.user, {'my_datasets': 'True', 'active': 'True'})
        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0].id, self.dpou_contracten_api.id)


class GetActiveDatasetsPerInterfaceForUsersOrgUnitsTests(TestCase):

    def setUp(self):
        pass

    @patch('rm.view_util.user_utils')
    def test_empty_no_org_interface_defs(self, mock_user_utils):
        mock_user = Mock()
        mock_user_utils.get_all_org_units_of_user.return_value = []
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)
        self.assertEqual(result[0].system, "Negometrix")
        self.assertEqual(result[0].dataset_type, "Contracten")

    @patch('rm.view_util.user_utils')
    def test_one_org_one_interfaces_def(self, mock_user_utils):
        # STATIC
        system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")[0]

        mock_user_utils.get_all_org_units_of_user.return_value = [org_unit_iaas, ]

        expected_record = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name)

        mock_user = Mock()
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = URL_NAME_CONTRACTEN_UPLOAD
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected_record)

    @patch('rm.view_util.user_utils')
    def test_one_org_one_interfaces_def_one_call(self, mock_user_utils):
        # STATIC
        system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")[0]

        # PROCESS
        call = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                            user_email="b.de.graaf@npo.nl",
                                            status=InterfaceCall.ACTIVE)

        mock_user_utils.get_all_org_units_of_user.return_value = [org_unit_iaas, ]
        expected_record = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="b.de.graaf@npo.nl")

        mock_user = Mock()
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = URL_NAME_CONTRACTEN_UPLOAD
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected_record)

    @patch('rm.view_util.user_utils')
    def test_one_org_one_interfaces_def_one_call_one_dpou(self, mock_user_utils):
        # STATIC
        system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")[0]

        # PROCESS
        call = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                            user_email="b.de.graaf@npo.nl",
                                            status=InterfaceCall.ACTIVE)
        dpou = DataPerOrgUnit.objects.create(interface_call=call,
                                             org_unit=org_unit_iaas,
                                             number_of_data_rows_ok=10,
                                             number_of_data_rows_warning=5,
                                             active=True)

        # return IaaS as org_unit of the user
        mock_user_utils.get_all_org_units_of_user.return_value = [org_unit_iaas, ]
        expected_record = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="b.de.graaf@npo.nl",
            org_unit=org_unit_iaas.name,
            rows_ok=10,
            rows_warning=5)

        mock_user = Mock()
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = URL_NAME_CONTRACTEN_UPLOAD
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected_record)

    @patch('rm.view_util.user_utils')
    def test_one_org_one_interfaces_def_one_call_two_dpou_one_valid(self, mock_user_utils):
        # STATIC
        system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")[0]
        org_unit_xxxx = OrganizationalUnit.objects.get_or_create(name="Pt: XxxX")[0]

        # PROCESS
        call = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                            user_email="b.de.graaf@npo.nl",
                                            status=InterfaceCall.ACTIVE)
        dpou = DataPerOrgUnit.objects.create(interface_call=call,
                                             org_unit=org_unit_iaas,
                                             number_of_data_rows_ok=10,
                                             number_of_data_rows_warning=5,
                                             active=True)
        # A DPOU for a org unit not in users resp.
        dpou_xxxx = DataPerOrgUnit.objects.create(interface_call=call,
                                                  org_unit=org_unit_xxxx,
                                                  number_of_data_rows_ok=20,
                                                  number_of_data_rows_warning=25,
                                                  active=True)

        # return IaaS as org_unit of the user
        mock_user_utils.get_all_org_units_of_user.return_value = [org_unit_iaas, ]
        expected_record = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="b.de.graaf@npo.nl",
            org_unit=org_unit_iaas.name,
            rows_ok=10,
            rows_warning=5)

        mock_user = Mock()
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = URL_NAME_CONTRACTEN_UPLOAD
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected_record)

    @patch('rm.view_util.user_utils')
    def test_one_org_one_interfaces_def_one_call_two_dpou_two_valid(self, mock_user_utils):
        # STATIC
        system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")[0]
        org_unit_xxxx = OrganizationalUnit.objects.get_or_create(name="Pt: XxxX")[0]

        # PROCESS
        call = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                            user_email="b.de.graaf@npo.nl",
                                            status=InterfaceCall.ACTIVE)
        dpou = DataPerOrgUnit.objects.create(interface_call=call,
                                             org_unit=org_unit_iaas,
                                             number_of_data_rows_ok=10,
                                             number_of_data_rows_warning=5,
                                             active=True)

        # A DPOU for a org unit not in users resp.
        dpou_xxxx = DataPerOrgUnit.objects.create(interface_call=call,
                                                  org_unit=org_unit_xxxx,
                                                  number_of_data_rows_ok=20,
                                                  number_of_data_rows_warning=25,
                                                  active=True)

        # return IaaS and XxxX as org_unit of the user
        mock_user_utils.get_all_org_units_of_user.return_value = [org_unit_iaas,
                                                                  org_unit_xxxx]
        expected_record_0 = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="b.de.graaf@npo.nl",
            org_unit=org_unit_iaas.name,
            rows_ok=10,
            rows_warning=5)
        expected_record_1 = InterfaceListRecord(
            nr=2,
            interface_type="",
            url_upload_page="",
            dataset_type="",
            system="",
            date_time="",
            user_email="",
            org_unit=org_unit_xxxx.name,
            rows_ok=20,
            rows_warning=25)

        mock_user = Mock()
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = URL_NAME_CONTRACTEN_UPLOAD
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], expected_record_0)
        self.assertEqual(result[1], expected_record_1)

    @patch('rm.view_util.user_utils')
    def test_one_org_one_interfaces_def_one_call_two_dpou_two_valid_one_inactive_call(self, mock_user_utils):
        # STATIC
        system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")[0]
        org_unit_xxxx = OrganizationalUnit.objects.get_or_create(name="Pt: XxxX")[0]

        # PROCESS
        call = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                            user_email="b.de.graaf@npo.nl",
                                            status=InterfaceCall.ACTIVE)

        dpou = DataPerOrgUnit.objects.create(interface_call=call,
                                             org_unit=org_unit_iaas,
                                             number_of_data_rows_ok=10,
                                             number_of_data_rows_warning=5,
                                             active=True)

        # A DPOU for a org unit not in users resp.
        dpou_xxxx = DataPerOrgUnit.objects.create(interface_call=call,
                                                  org_unit=org_unit_xxxx,
                                                  number_of_data_rows_ok=20,
                                                  number_of_data_rows_warning=25,
                                                  active=True)
        # Inactive Call
        call_2 = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                              user_email="b.de.graaf@npo.nl",
                                              status=InterfaceCall.INACTIVE)

        # return IaaS and XxxX as org_unit of the user
        mock_user_utils.get_all_org_units_of_user.return_value = [org_unit_iaas,
                                                                  org_unit_xxxx]
        expected_record_0 = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="b.de.graaf@npo.nl",
            org_unit=org_unit_iaas.name,
            rows_ok=10,
            rows_warning=5)
        expected_record_1 = InterfaceListRecord(
            nr=2,
            interface_type="",
            url_upload_page="",
            dataset_type="",
            system="",
            date_time="",
            user_email="",
            org_unit=org_unit_xxxx.name,
            rows_ok=20,
            rows_warning=25)

        mock_user = Mock()
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = URL_NAME_CONTRACTEN_UPLOAD
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], expected_record_0)
        self.assertEqual(result[1], expected_record_1)

    @patch('rm.view_util.user_utils')
    def test_one_org_one_interfaces_def_one_call_two_dpou_two_valid_one_active_call(self, mock_user_utils):
        # STATIC
        system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")[0]
        org_unit_xxxx = OrganizationalUnit.objects.get_or_create(name="Pt: XxxX")[0]

        # PROCESS
        call = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                            user_email="b.de.graaf@npo.nl",
                                            status=InterfaceCall.ACTIVE)

        dpou = DataPerOrgUnit.objects.create(interface_call=call,
                                             org_unit=org_unit_iaas,
                                             number_of_data_rows_ok=10,
                                             number_of_data_rows_warning=5,
                                             active=True)

        # A DPOU for a org unit not in users resp.
        dpou_xxxx = DataPerOrgUnit.objects.create(interface_call=call,
                                                  org_unit=org_unit_xxxx,
                                                  number_of_data_rows_ok=20,
                                                  number_of_data_rows_warning=25,
                                                  active=True)
        # Inactive Call
        call_2 = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                              user_email="b2.de.graaf@npo.nl",
                                              status=InterfaceCall.ACTIVE)

        # return IaaS and XxxX as org_unit of the user
        mock_user_utils.get_all_org_units_of_user.return_value = [org_unit_iaas,
                                                                  org_unit_xxxx]
        expected_record_0 = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="b.de.graaf@npo.nl",
            org_unit=org_unit_iaas.name,
            rows_ok=10,
            rows_warning=5)
        expected_record_1 = InterfaceListRecord(
            nr=2,
            interface_type="",
            url_upload_page="",
            dataset_type="",
            system="",
            date_time="",
            user_email="",
            org_unit=org_unit_xxxx.name,
            rows_ok=20,
            rows_warning=25)
        expected_record_2 = InterfaceListRecord(
            nr=3,
            interface_type="",
            url_upload_page="",
            dataset_type="",
            system="",
            date_time="",
            user_email="b2.de.graaf@npo.nl",
            org_unit="",
            rows_ok="",
            rows_warning="")

        mock_user = Mock()
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = URL_NAME_CONTRACTEN_UPLOAD
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], expected_record_0)
        self.assertEqual(result[1], expected_record_1)
        self.assertEqual(result[2], expected_record_2)

    @patch('rm.view_util.user_utils')
    def test_one_org_one_interfaces_def_one_call_two_dpou_two_valid_one_active_call_one_def(self, mock_user_utils):
        # STATIC
        system_negometrix, created = System.objects.get_or_create(name=NEGOMETRIX)
        dataset_type_contracten, created = DataSetType.objects.get_or_create(name=CONTRACTEN)
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas, created = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")
        org_unit_xxxx, created = OrganizationalUnit.objects.get_or_create(name="Pt: XxxX")

        # PROCESS
        call = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                            user_email="b.de.graaf@npo.nl",
                                            status=InterfaceCall.ACTIVE)

        dpou = DataPerOrgUnit.objects.create(interface_call=call,
                                             org_unit=org_unit_iaas,
                                             number_of_data_rows_ok=10,
                                             number_of_data_rows_warning=5,
                                             active=True)

        # A DPOU for a org unit not in users resp.
        dpou_xxxx = DataPerOrgUnit.objects.create(interface_call=call,
                                                  org_unit=org_unit_xxxx,
                                                  number_of_data_rows_ok=20,
                                                  number_of_data_rows_warning=25,
                                                  active=True)
        # Inactive Call
        call_2 = InterfaceCall.objects.create(interface_definition=interface_def_nego_contr,
                                              user_email="b2.de.graaf@npo.nl",
                                              status=InterfaceCall.ACTIVE)

        # A random system, dataset_type and int_def
        system_test = System.objects.get_or_create(name="TestSystem")[0]
        dataset_type_tests = DataSetType.objects.get_or_create(name="Tests")[0]
        interface_def_test = InterfaceDefinition.objects. \
            get_or_create(name="Tests upload",
                          system=system_test,
                          data_set_type=dataset_type_tests,
                          interface_type=InterfaceDefinition.UPLOAD)[0]

        # return IaaS and XxxX as org_unit of the user
        mock_user_utils.get_all_org_units_of_user.return_value = [org_unit_iaas,
                                                                  org_unit_xxxx]
        expected_record_0 = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="b.de.graaf@npo.nl",
            org_unit=org_unit_iaas.name,
            rows_ok=10,
            rows_warning=5)
        expected_record_1 = InterfaceListRecord(
            nr=2,
            interface_type="",
            url_upload_page="",
            dataset_type="",
            system="",
            date_time="",
            user_email="",
            org_unit=org_unit_xxxx.name,
            rows_ok=20,
            rows_warning=25)
        expected_record_2 = InterfaceListRecord(
            nr=3,
            interface_type="",
            url_upload_page="",
            dataset_type="",
            system="",
            date_time="",
            user_email="b2.de.graaf@npo.nl",
            org_unit="",
            rows_ok="",
            rows_warning="")
        expected_record_3 = InterfaceListRecord(
            nr=4,
            interface_type=interface_def_test.get_interface_type_display(),
            url_upload_page=reverse(URL_NAME_CONTRACTEN_UPLOAD),
            dataset_type=interface_def_test.data_set_type.name,
            system=interface_def_test.system.name)

        mock_user = Mock()
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = URL_NAME_CONTRACTEN_UPLOAD
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], expected_record_0)
        self.assertEqual(result[1], expected_record_1)
        self.assertEqual(result[2], expected_record_2)
        self.assertEqual(result[3], expected_record_3)

    @patch('rm.view_util.user_utils')
    def test_no_permission(self, mock_user_utils):
        # STATIC
        system_negometrix, created = System.objects.get_or_create(name=NEGOMETRIX)
        dataset_type_contracten, created = DataSetType.objects.get_or_create(name=CONTRACTEN)
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas, created = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")
        org_unit_xxxx, created = OrganizationalUnit.objects.get_or_create(name="Pt: XxxX")

        # return IaaS and XxxX as org_unit of the user
        mock_user_utils.get_all_org_units_of_user.return_value = []
        expected_record_0 = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page="",
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="",
            org_unit="",
            rows_ok="",
            rows_warning="")

        mock_user = Mock()
        # mock_user.is_superuser.return_value = False
        # mock_user.has_perm_with_name.return_value = False
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = None
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected_record_0)

    @patch('rm.view_util.user_utils')
    def test_no_reverse_defined(self, mock_user_utils):
        # STATIC
        system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        dataset_type_contracten = DataSetType.objects.get_or_create(name=CONTRACTEN)[0]
        interface_def_nego_contr = InterfaceDefinition.objects.get(name="Contracten upload")
        org_unit_iaas = OrganizationalUnit.objects.get_or_create(name="Pt: IaaS")[0]
        org_unit_xxxx = OrganizationalUnit.objects.get_or_create(name="Pt: XxxX")[0]

        # return IaaS and XxxX as org_unit of the user
        mock_user_utils.get_all_org_units_of_user.return_value = []
        expected_record_0 = InterfaceListRecord(
            nr=1,
            interface_type=interface_def_nego_contr.get_interface_type_display(),
            url_upload_page="",
            dataset_type=interface_def_nego_contr.data_set_type.name,
            system=interface_def_nego_contr.system.name,
            date_time="whatever, not checked",
            user_email="",
            org_unit="",
            rows_ok="",
            rows_warning="")

        mock_user = Mock()
        # mock_user.is_superuser.return_value = False
        # mock_user.has_perm_with_name.return_value = False
        mock_user.get_url_name_for_rm_function_if_has_permission.return_value = "UNKNOWN"
        result = get_active_datasets_per_interface_for_users_org_units(mock_user)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], expected_record_0)


class GenericFileUploadTests(TestCase):

    def setUp(self):
        set_up_user_and_login(self, superuser=True)

    def test_upload_empty_file_with_xls(self):
        nr_int_calls_before = len(InterfaceCall.objects.all())
        file = open("rm/test/resources/EmptyFileWithXLSExtension.xls", "rb")
        id, status, msg = process_file(file, self.user)
        nr_int_calls_after = len(InterfaceCall.objects.all())
        self.assertEqual(nr_int_calls_after, nr_int_calls_before + 1)

        interface_call: InterfaceCall = InterfaceCall.objects.last()
        self.assertEqual(interface_call.filename, "rm/test/resources/EmptyFileWithXLSExtension.xls")
        self.assertTrue(interface_call.message.__contains__('Het openen van dit bestand als excel bestand '
                                                            'geeft een foutmelding: File is not a zip file'))


class SetSessionTimeoutInactivityTests(TestCase):

    def setUp(self):
        pass

    def test_set_session_timeout_no_arg(self):
        mock_request = Mock()
        view_util.set_session_timeout_inactivity(mock_request)
        mock_request.session.set_expiry.assert_called_with(5*60)

    def test_set_session_timeout_arg_None(self):
        mock_request = Mock()
        view_util.set_session_timeout_inactivity(mock_request, None)
        mock_request.session.set_expiry.assert_called_with(20*60)

    def test_set_session_timeout_NEVER(self):
        mock_request = Mock()
        view_util.set_session_timeout_inactivity(mock_request, "NEVER")
        mock_request.session.set_expiry.assert_not_called()

    def test_set_session_timeout_with_10_minutes(self):
        mock_request = Mock()
        view_util.set_session_timeout_inactivity(mock_request, 10)
        mock_request.session.set_expiry.assert_called_with(600)

    def test_set_session_timeout_with_illegal_arg(self):
        mock_request = Mock()
        view_util.set_session_timeout_inactivity(mock_request, "ILLEGAL")
        mock_request.session.set_expiry.assert_called_with(20*60)


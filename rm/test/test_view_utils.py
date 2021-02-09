from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.shortcuts import get_object_or_404

from rm.constants import NEGOMETRIX, CONTRACTEN
from rm.models import System, DataSetType, InterfaceDefinition, DataPerOrgUnit, InterfaceCall
from rm.view_util import create_addition_dataset_filter, get_datasets_for_user
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
        params = {'active': 'FAlse'}
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

    def test_create_addition_dataset_filter_negometrix(self):
        params = {'system': 'Negometrix'}
        expected_filter = {'interface_call__interface_definition__system_id': self.system_negometrix.id}

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
        params = {'responsibility': 'user'}
        user_responsible_interface_names = ['Contracten upload', ]
        expected_filter = {'interface_call__interface_definition__name__in': user_responsible_interface_names}

        result_filter = create_addition_dataset_filter(self.user, params)
        self.assertEqual(result_filter, expected_filter)

    def test_create_addition_dataset_filter_responsibility_no_permissions(self):
        params = {'responsibility': 'user'}
        user_responsible_interface_names = []
        expected_filter = {'interface_call__interface_definition__name__in': user_responsible_interface_names}

        result_filter = create_addition_dataset_filter(self.user_without_permissions, params)
        self.assertEqual(result_filter, expected_filter)


class ViewUtilTests(TestCase):

    def setUp(self):
        self.content_type_interface_call = ContentType.objects.get_for_model(InterfaceCall)
        permission_contracten_upload = Permission.objects.get_or_create(codename="contracten_upload",
                                                                        name="Contracten upload",
                                                                        content_type=self.content_type_interface_call)
        self.user = CustomUser.objects.create(username="TestUser1")
        self.user.user_permissions.add(permission_contracten_upload[0])

        # STATICS: System, DatasetType
        self.system_negometrix = System.objects.get_or_create(name=NEGOMETRIX)[0]
        self.data_set_type, create = DataSetType.objects.get_or_create(name=CONTRACTEN)

    def test_get_datasets_for_user_on_org_authorization(self):
        # Interface Definition
        self.interface_definition = InterfaceDefinition.objects.create(system=self.system_negometrix,
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
        self.assertEqual(datasets[0].id, self.dpou_1.id)     # Failed a couple of times when I ran all tests
        self.assertEqual(datasets[1].id, self.dpou_3.id)     # But suddenly went ok again.

        # PRE-ACTION: add another dpou, for the team (under cluster1, so visible)
        self.dpou_4 = DataPerOrgUnit.objects.create(org_unit=self.org_unit_t1,
                                                    interface_call=self.interface_call,
                                                    active=True)

        # ACTION: get datasets visible for this user again
        datasets = get_datasets_for_user(self.user, {'active': 'All'})

        # POST: now 3:
        self.assertEqual(len(datasets), 3)
        self.assertEqual(datasets[0].id, self.dpou_1.id)
        self.assertEqual(datasets[1].id, self.dpou_3.id)
        self.assertEqual(datasets[2].id, self.dpou_4.id)

        # ACTION: get datasets visible for this user ACTIVE
        datasets = get_datasets_for_user(self.user, {'active': 'True'})

        # POST: now 2:
        self.assertEqual(len(datasets), 2)
        self.assertEqual(datasets[0].id, self.dpou_1.id)
        # self.assertEqual(datasets[1].id, self.dpou_3.id)
        self.assertEqual(datasets[1].id, self.dpou_4.id)

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
        self.int_def_contracten_upload = InterfaceDefinition.objects.create(name="Contracten upload",
                                                                            system=self.system_negometrix,
                                                                            data_set_type=self.data_set_type,
                                                                            interface_type=InterfaceDefinition.UPLOAD)

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

        # Test System for uploadin Tests
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
        datasets = get_datasets_for_user(self.user, {'responsibility': 'user'})
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
        datasets = get_datasets_for_user(self.user, {'responsibility': 'user'})
        self.assertEqual(len(datasets), 2)
        self.assertEqual(datasets[0].id, self.dpou_contracten_upload.id)
        self.assertEqual(datasets[1].id, self.dpou_contracten_api.id)

        # Now test if we can use the filters mixed: responsibility and active
        self.dpou_contracten_upload.active = False
        self.dpou_contracten_upload.save()

        datasets = get_datasets_for_user(self.user, {'responsibility': 'user', 'active': 'All'})
        self.assertEqual(len(datasets), 2)
        self.assertEqual(datasets[0].id, self.dpou_contracten_upload.id)
        self.assertEqual(datasets[1].id, self.dpou_contracten_api.id)

        datasets = get_datasets_for_user(self.user, {'responsibility': 'user', 'active': 'True'})
        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0].id, self.dpou_contracten_api.id)

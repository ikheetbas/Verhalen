from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase

from rm.test.test_util import create_user
from users.models import OrganizationalUnit, CustomUser, convert_permission_name_to_id
from users.user_utils import all_org_units_of_org_unit, get_all_org_units_of_user, get_user_responsible_interface_names


class AllOrgUnitsOfAUserTests(TestCase):

    def setUp(self):
        self.dep_1 = OrganizationalUnit.objects.get_or_create(name="dep1",
                                                              type=OrganizationalUnit.AFDELING)[0]

        self.cluster1 = OrganizationalUnit.objects.get_or_create(name="cluster1",
                                                                 type=OrganizationalUnit.CLUSTER,
                                                                 parent_org_unit=self.dep_1)[0]

        self.team1_1 = OrganizationalUnit.objects.get_or_create(name="team1.1",
                                                                parent_org_unit=self.cluster1)[0]

        self.team1_2 = OrganizationalUnit.objects.get_or_create(name="team1.2",
                                                                parent_org_unit=self.cluster1)[0]

        self.cluster2 = OrganizationalUnit.objects.get_or_create(name="cluster2",
                                                                 type=OrganizationalUnit.CLUSTER,
                                                                 parent_org_unit=self.dep_1)[0]

        self.team2_1 = OrganizationalUnit.objects.get_or_create(name="team2.1",
                                                                parent_org_unit=self.cluster2)[0]

        self.team2_2 = OrganizationalUnit.objects.get_or_create(name="team2.2",
                                                                parent_org_unit=self.cluster2)[0]

        self.team1_1_manager = CustomUser.objects.create(username="TM1")
        self.team1_1.customuser_set.add(self.team1_1_manager)

        self.team2_2_manager = CustomUser.objects.create(username="TM2")
        self.team2_1.customuser_set.add(self.team2_2_manager)
        self.team2_2.customuser_set.add(self.team2_2_manager)

        self.cluster1_manager = CustomUser.objects.create(username="CM1")
        self.cluster1.customuser_set.add(self.cluster1_manager)

        self.dep1_manager = CustomUser.objects.create(username="DM1")
        self.dep_1.customuser_set.add(self.dep1_manager)

    def test_all_orgs_of_team(self):
        result = all_org_units_of_org_unit(self.team1_2)
        expected = [self.team1_2, ]
        self.assertEqual(result, expected)

    def test_all_orgs_of_cluster(self):
        result = all_org_units_of_org_unit(self.cluster1)
        expected = [self.cluster1, self.team1_1, self.team1_2]
        self.assertEqual(result, expected)

    def test_all_orgs_of_dep(self):
        result = all_org_units_of_org_unit(self.dep_1)
        expected = [self.dep_1, self.cluster1, self.team1_1, self.team1_2,
                    self.cluster2, self.team2_1, self.team2_2]
        self.assertEqual(result, expected)

    def test_all_orgs_of_team_manager_with_1_team(self):
        result = get_all_org_units_of_user(self.team1_1_manager)
        expected = [self.team1_1, ]
        self.assertEqual(result, expected)

    def test_all_orgs_of_team_manager_with_2_teams(self):
        result = get_all_org_units_of_user(self.team2_2_manager)
        expected = [self.team2_1, self.team2_2]
        self.assertEqual(result, expected)

    def test_all_orgs_of_clustermanager(self):
        result = get_all_org_units_of_user(self.cluster1_manager)
        expected = [self.cluster1, self.team1_1, self.team1_2]
        self.assertEqual(result, expected)

    def test_all_orgs_of_dep_manager(self):
        result = get_all_org_units_of_user(self.dep1_manager)
        expected = [self.dep_1,
                    self.cluster1, self.team1_1, self.team1_2,
                    self.cluster2, self.team2_1, self.team2_2]
        self.assertEqual(result, expected)


class UserPermissionTests(TestCase):

    def test_convert_permission_name(self):
        app = "rm"
        name = "Contracten Upload"

        expected = "rm.contracten_upload"
        result = convert_permission_name_to_id(app, name)
        self.assertEqual(result, expected)

    def test_has_user_permission_with_name(self):
        user = CustomUser.objects.create(username="Inkoper")
        permission = Permission.objects.get(name="Contracten upload")
        user.user_permissions.add(permission)

        self.assertTrue(user.has_perm_with_name("rm", "Contracten upload"))

    def test_get_user_responsible_interface_names_with_zero_interface_permissions(self):
        self.user = create_user(username="No Body")
        permission_names = get_user_responsible_interface_names(self.user)
        self.assertTrue(len(permission_names) == 0)

    def test_get_user_responsible_interface_names_with_contract_api_and_upload(self):
        self.user = create_user(group_name="Buyer",
                                username="I. koper")
        permission_names = get_user_responsible_interface_names(self.user)
        self.assertTrue("Contracten API" in permission_names)
        self.assertTrue("Contracten upload" in permission_names)

    def test_get_user_responsible_interface_names_superuser(self):
        self.user = get_user_model().objects.create(username="Superman",
                                                    is_superuser=True,
                                                    is_active=True)
        permission_names = get_user_responsible_interface_names(self.user)
        self.assertTrue("Contracten API" in permission_names)
        self.assertTrue("Contracten upload" in permission_names)


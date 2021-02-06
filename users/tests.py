from django.contrib.auth import get_user_model
from django.test import TestCase

from users.models import OrganizationalUnit, CustomUser
from users.user_utils import all_org_units_of_org_unit, get_all_org_units_of_user


class CustomUserTests(TestCase):

    def test_create_user(self):
        User = get_user_model()  # through this method we get the object defined
        # in the settings.py
        user = User.objects.create_user(
            username='will',
            email='will@email.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'will')
        self.assertEqual(user.email, 'will@email.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@email.com',
            password='testpass123'
        )
        self.assertEqual(admin_user.username, 'superadmin')
        self.assertEqual(admin_user.email, 'superadmin@email.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class UserUtilTests(TestCase):

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
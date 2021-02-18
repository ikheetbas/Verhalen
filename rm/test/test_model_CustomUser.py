from django.test import TestCase

from users.models import CustomUser, OrganizationalUnit


class DoesUserBelongToOneOrgUnitTests(TestCase):

    def test_user_with_no_org(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        self.assertFalse(lonely_user.has_perm_for_org_unit(a_team))

    def test_user_with_right_org_unit(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        lonely_user.org_units.add(a_team)
        self.assertTrue(lonely_user.has_perm_for_org_unit(a_team))

    def test_user_with_other_org_unit(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        lonely_user.org_units.add(a_team)
        self.assertFalse(lonely_user.has_perm_for_org_unit(b_team))

    def test_user_with_cluster_with_a_team(self):
        cluster_chef = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        a_cluster = OrganizationalUnit.objects.create(name="A-cluster", type=OrganizationalUnit.CLUSTER)
        a_team.parent_org_unit = a_cluster
        cluster_chef.org_units.add(a_cluster)
        self.assertTrue(cluster_chef.has_perm_for_org_unit(a_cluster))
        self.assertTrue(cluster_chef.has_perm_for_org_unit(a_team))

    def test_user_with_cluster_with_a_team_2(self):
        dep_chef = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        a_cluster = OrganizationalUnit.objects.create(name="A-cluster", type=OrganizationalUnit.CLUSTER)
        a_departement = OrganizationalUnit.objects.create(name="A-department", type=OrganizationalUnit.AFDELING)
        a_team.parent_org_unit = a_cluster
        a_cluster.parent_org_unit = a_departement
        dep_chef.org_units.add(a_departement)
        self.assertTrue(dep_chef.has_perm_for_org_unit(a_departement))
        self.assertTrue(dep_chef.has_perm_for_org_unit(a_cluster))
        self.assertTrue(dep_chef.has_perm_for_org_unit(a_team))
        self.assertFalse(dep_chef.has_perm_for_org_unit(b_team))

    def test_loop_beveiliging(self):
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        a_team.parent_org_unit = b_team
        b_team.parent_org_unit = a_team
        a_cluster = OrganizationalUnit.objects.create(name="A-cluster", type=OrganizationalUnit.CLUSTER)
        a_departement = OrganizationalUnit.objects.create(name="A-department", type=OrganizationalUnit.AFDELING)
        dep_chef = CustomUser.objects.create(username="Lonely")
        dep_chef.org_units.add(a_departement)
        with self.assertRaises(Exception):
            dep_chef.has_perm_for_org_unit(a_team)


class DoesUserBelongToTwoOrgUnitTests(TestCase):

    def test_user_with_2_right_org_units(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        lonely_user.org_units.add(a_team)
        lonely_user.org_units.add(b_team)
        self.assertTrue(lonely_user.has_perm_for_org_unit(a_team, b_team))

    def test_user_with_1_missing_org_units(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        lonely_user.org_units.add(a_team)
        self.assertFalse(lonely_user.has_perm_for_org_unit(a_team, b_team))

    def test_user_with_2_org_units_but_1_missing_org_units(self):
        lonely_user = CustomUser.objects.create(username="Lonely")
        a_team = OrganizationalUnit.objects.create(name="A-Team", type=OrganizationalUnit.TEAM)
        b_team = OrganizationalUnit.objects.create(name="B-Team", type=OrganizationalUnit.TEAM)
        c_team = OrganizationalUnit.objects.create(name="C-Team", type=OrganizationalUnit.TEAM)
        lonely_user.org_units.add(a_team)
        lonely_user.org_units.add(c_team)
        self.assertFalse(lonely_user.has_perm_for_org_unit(a_team, b_team))
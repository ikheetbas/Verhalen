from django.test import TestCase

from rm.models import System, Mapping
from users.models import OrganizationalUnit


class SystemGetOrgUnitByMappingTests(TestCase):

    def setUp(self):
        self.system_a = System.objects.create(name="SYSTEM_A")
        self.org_unit = OrganizationalUnit.objects.create(name="MyTeam",
                                                          type=OrganizationalUnit.TEAM)

    def test_get_org_unit_found_by_system(self):
        mapping_name = "my_map"
        mapping = Mapping.objects.create(name=mapping_name,
                                         system=self.system_a,
                                         org_unit=self.org_unit)
        found_org_unit = self.system_a.get_org_unit_by_mapping(mapping_name)
        self.assertEqual(self.org_unit.name, found_org_unit.name)

    def test_get_org_unit_found_by_system_name(self):
        mapping_name = "my_map"
        mapping = Mapping.objects.create(name=mapping_name,
                                         system=self.system_a,
                                         org_unit=self.org_unit)
        found_org_unit = self.system_a.get_org_unit_by_mapping(mapping_name)
        self.assertEqual(self.org_unit.name, found_org_unit.name)

    def test_get_org_unit_unknown_mapping(self):
        not_existing_mapping_name = "Not existing"
        mapping_name = "my_map"
        mapping = Mapping.objects.create(name=mapping_name,
                                         system=self.system_a,
                                         org_unit=self.org_unit)
        found_org_unit = self.system_a.get_org_unit_by_mapping(not_existing_mapping_name)
        self.assertIsNone(found_org_unit)
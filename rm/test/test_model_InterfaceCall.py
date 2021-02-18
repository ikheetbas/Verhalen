from django.test import TestCase

from rm.models import InterfaceCall, DataPerOrgUnit
from rm.test.test_util import set_up_user_and_login
from users.models import OrganizationalUnit


class InterfaceCallTests(TestCase):

    def setUp(self):
        set_up_user_and_login(self)

    def test_org_units_none(self):
        interface_call_1 = InterfaceCall.objects.create()
        org_units = interface_call_1.org_units
        self.assertTrue(len(org_units) == 0)

    def test_org_units_one(self):
        interface_call_1 = InterfaceCall.objects.create()
        org_unit_1 = OrganizationalUnit.objects.create(name="AFD1")
        dpou = DataPerOrgUnit.objects.create(interface_call=interface_call_1,
                                             org_unit=org_unit_1)
        org_units = interface_call_1.org_units
        self.assertTrue(len(org_units) == 1)
        self.assertTrue(org_units[0] == org_unit_1)

    def test_org_units_2(self):
        interface_call_1 = InterfaceCall.objects.create()
        org_unit_1 = OrganizationalUnit.objects.create(name="AFD1")
        org_unit_2 = OrganizationalUnit.objects.create(name="AFD2")
        dpou1 = DataPerOrgUnit.objects.create(interface_call=interface_call_1,
                                              org_unit=org_unit_1)
        dpou2 = DataPerOrgUnit.objects.create(interface_call=interface_call_1,
                                              org_unit=org_unit_2)
        org_units = interface_call_1.org_units
        self.assertTrue(len(org_units) == 2)
        self.assertTrue( org_unit_1 in org_units)
        self.assertTrue( org_unit_2 in org_units)
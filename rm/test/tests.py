from django.test import TestCase

from stage.models import StageContract

from .test_util import set_up_user_with_interface_call_and_contract


class DataModelTest(TestCase):

    def setUp(self):
        set_up_user_with_interface_call_and_contract(self)

    def test_stage_contract(self):
        expected = 'StageContract: NL-123: Test contract naam'
        self.assertEqual(self.stage_contract_1.__str__(), expected)

    def testContractsOfInterfaceCall_one_contract(self):
        contracts = self.interface_call_1.stage_contracts()
        self.assertEqual(len(contracts), 1)

    def testContractsOfInterfaceCall_two_contracts(self):
        self.stage_contract_2 = StageContract.objects.create(contract_nr='NL-123',
                                                             seq_nr=0,
                                                             description='Test Contract 2',
                                                             contract_owner='T. Ester',
                                                             contract_name='Test contract naam',
                                                             data_per_org_unit=self.data_per_org_unit)

        contracts = self.interface_call_1.stage_contracts()
        self.assertEqual(len(contracts), 2)



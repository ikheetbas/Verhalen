from django.db.models.functions import Now
from django.test import TestCase

from .models import Contract, InterfaceCall

class ContractTest(TestCase):

    def test_home_page_with_contracts(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)

    def test_create_interface_call(self):
        now = Now()
        interfaceCall = InterfaceCall(status='Test',
                                      date_time_creation=now,
                                      filename='test.xls')
        self.assertTrue(isinstance(interfaceCall, InterfaceCall))

    def test_create_contract_with_parent(self):
        now = Now()
        interfaceCall = InterfaceCall(status='Test',
                                      date_time_creation=now,
                                      filename='test.xls')
        interfaceCall.save()
        contract = Contract(contract_nr="NL-123",
                            interface_call=interfaceCall)
        contract.save()
        self.assertTrue(isinstance(contract, Contract))

    def test_create_contract_without_parent(self):
        contract = Contract(contract_nr="NL-123")
        with self.assertRaises(Exception):
            contract.save()

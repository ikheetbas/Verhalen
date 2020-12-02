from django.db.models.functions import Now
from django.test import TestCase

from .models import Contract, InterfaceCall
from django.db.utils import IntegrityError

class ContractTest(TestCase):

    def test_homepage(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)

    def test_one_contract_on_page(self):
        interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                     status='TestStatus',
                                                     filename='Text.xls')
        Contract.objects.create(contract_nr='NL-123',
                                description='Test Contract',
                                contract_owner='T. Ester',
                                interface_call=interfaceCall)
        response = self.client.get('/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester')

    def test_two_contracts_on_page(self):
        interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                     status='TestStatus',
                                                     filename='Text.xls')
        Contract.objects.create(contract_nr='NL-123',
                                description='Test Contract',
                                contract_owner='T. Ester',
                                interface_call=interfaceCall)
        Contract.objects.create(contract_nr='NL-345',
                                description='Test Contract 2',
                                contract_owner='T. Ester',
                                interface_call=interfaceCall)
        response = self.client.get('/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester', count=2)

        self.assertContains(response, 'NL-345')
        self.assertContains(response, 'Test Contract 2')

    def test_create_contract_without_parent(self):
        try:
            Contract.objects.create(contract_nr="NL-123")
        except IntegrityError as exception:
            expected = "null value in column \"interface_call_id\" " \
                       "violates not-null constraint"
            self.assertTrue(expected in exception.__str__())


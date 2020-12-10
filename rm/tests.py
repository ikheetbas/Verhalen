from django.db.models.functions import Now
from django.test import TestCase
from openpyxl import Workbook, load_workbook

from .constants import ERROR_MSG_FILE_DEFINITION_ERROR, ERROR
from .models import Contract, InterfaceCall
from django.db.utils import IntegrityError

from .files import file_is_excel_file, file_has_excel_extension, is_valid_header_row, handle_uploaded_excel_file, \
    get_field_positions, get_mandatory_field_positions, get_headers
from .negometrix import mandatory_fields_present, register_contract


class ContractTest(TestCase):

    def setUp(self):
        self.interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                          status='TestStatus',
                                                          filename='Text.xls')
        self.conctract_1 = Contract.objects.create(contract_nr='NL-123',
                                                   seq_nr=0,
                                                   description='Test Contract',
                                                   contract_owner='T. Ester',
                                                   interface_call=self.interfaceCall,
                                                   contract_name='Test contract naam')

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_contract(self):
        expected = 'NL-123: Test contract naam'
        self.assertEqual(self.conctract_1.__str__(), expected)

    def test_one_contract_on_page(self):
        response = self.client.get('/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester')

    def test_two_contracts_on_page(self):
        Contract.objects.create(contract_nr='NL-345',
                                seq_nr=1,
                                description='Test Contract 2',
                                contract_owner='T. Ester',
                                interface_call=self.interfaceCall)
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


class ExcelTests(TestCase):

    # Excel file extension

    def test_not_an_excel_file_extension(self):
        filename = 'test.txt'
        self.assertFalse(file_has_excel_extension(filename)[0])

    def test_an_excel_file_extension_xls(self):
        filename = 'test.xls'
        self.assertTrue(file_has_excel_extension(filename)[0])

    def test_an_excel_file_extension_XLS(self):
        filename = 'test.XLS'
        self.assertTrue(file_has_excel_extension(filename)[0])

    def test_an_excel_file_extension_xlsx(self):
        filename = 'test.xlsx'
        self.assertTrue(file_has_excel_extension(filename)[0])

    def test_an_excel_file_extension_XLSX(self):
        filename = 'test.XLSX'
        self.assertTrue(file_has_excel_extension(filename)[0])

    # Test on really being an Excel file, so can it be read as Workbook?

    def test_not_an_excelfile(self):
        file = open("rm/test/resources/aPdfWithExcelExtension.xls", "rb")
        print(f'type of file: {type(file)}')
        is_excel, msg = file_is_excel_file(file)
        self.assertFalse(is_excel, msg)

    def test_an_excelfile_xlsx(self):
        file = open("rm/test/resources/a_valid_excel_file.xlsx", "rb")
        print(f'type of file: {type(file)}')
        is_excel, msg = file_is_excel_file(file)
        self.assertTrue(is_excel, msg)

    # Test valid headers

    def test_valid_header_row_exact(self):
        self.assertTrue(is_valid_header_row(headers=('x', 'y', 'z'),
                                            required_headers=('x', 'z')))

    def test_valid_header_row_case_sensitive(self):
        self.assertTrue(is_valid_header_row(headers=('X', 'y', 'z'),
                                            required_headers=('x', 'z')))

    def test_invalid_header_row(self):
        self.assertFalse(is_valid_header_row(headers=('a', 'b', 'z'),
                                             required_headers=('x', 'z')))

    # Test handle uploaded excel file

    def test_upload_excel_file_invalid_headers(self):
        try:
            interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                         status='TestStatus',
                                                         filename='valid_excel_without_headers.xlsx')
            file = "rm/test/resources/valid_excel_without_headers.xlsx"
            handle_uploaded_excel_file(file, interfaceCall)
        except Exception as ex:
            self.assertTrue("header" in ex.__str__(),
                            f"We got another exception than expected, received: {ex.__str__()}")
        else:
            self.assertTrue(False, "No Exception, while expected because file has no headers")

    #  Test generic database functions

    def test_get_field_positions(self):

        available_headers = ['Header 1', "just a field", 'Header x', 'and another']
        defined_headers = dict(
            header_01="Header 1",
            zomaarwat="something",
            header_x="Header x",
        )
        field_positions = get_field_positions(available_headers,
                                              defined_headers)

        expected_field_opsitions = dict(
            header_01=0,
            header_x=2,
        )
        self.assertEqual(len(field_positions), 2)
        self.assertEqual(field_positions, expected_field_opsitions)

    def test_get_mandatory_field_postions_valid_situation(self):
        mandatory_fields = ("x", "z")
        field_positions = {"x": 1, "y": 2, "z": 4}
        positions = get_mandatory_field_positions(mandatory_fields,
                                                  field_positions)
        expected = [1, 4]
        self.assertEqual(positions, expected)

    def test_get_mandatory_field_postions_invalid_situation(self):
        mandatory_fields = ("x", "z")
        field_positions = {"x": 1, "y": 2, "b": 3}
        try:
            get_mandatory_field_positions(mandatory_fields,
                                          field_positions)
        except Exception as ex:
            self.assertEqual(ex.__str__(), ERROR_MSG_FILE_DEFINITION_ERROR)

    def test_mandatory_fields_present(self):
        mandatory_field_positions = [2, 3]
        row_values = ["nul", "een", "twee", "drie", "vier"]
        self.assertTrue(mandatory_fields_present(mandatory_field_positions,
                                                 row_values))

    def test_mandatory_fields_not_present_1_pos(self):
        mandatory_field_positions = [3]
        row_values = ["nul", "een", "twee", None, "vier"]
        self.assertFalse(mandatory_fields_present(mandatory_field_positions,
                                                  row_values))

    def test_mandatory_fields_not_present_1_ok_1_not(self):
        mandatory_field_positions = [2,3]
        row_values = ["nul", "een", "twee", None, "vier"]
        self.assertFalse(mandatory_fields_present(mandatory_field_positions,
                                                  row_values))

    def test_get_headers(self):
        file = open("rm/test/resources/test_get_headers.xlsx", "rb")
        workbook: Workbook = load_workbook(file)
        sheet = workbook.active
        headers = get_headers(sheet)
        expected = ("HEADER 1", "HEADER 2", None, "HEADER 4")
        self.assertEqual(headers, expected)

    def test_register_contract(self):
        row_nr = 4
        file = open("rm/test/resources/test_register_contract.xlsx", "rb")
        workbook: Workbook = load_workbook(file)
        sheet = workbook.active
        count = 1
        values_row_4 = []
        for row_values in sheet.iter_rows(min_row=1,
                                          min_col=1,
                                          values_only=True):
            if count == 4:
                values_row_4 = row_values
                break
            count+=1

        interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                     status='TestStatus',
                                                     filename='test_register_contract.xlsx')

        fields_with_position = dict( database_nr = 0,
                                     contract_nr = 1,
                                     contract_status = 2,
                                     description = 3,
                                     )

        mandatory_field_positions = (1,2)

        status, msg = register_contract(row_nr,
                                        values_row_4,
                                        interfaceCall,
                                        fields_with_position,
                                        mandatory_field_positions
                                        )

        expected_status = ERROR

        self.assertEqual(status, expected_status)

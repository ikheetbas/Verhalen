from django.conf import settings
from django.db.models.functions import Now
from django.test import TestCase
from openpyxl import Workbook, load_workbook

from .constants import ERROR_MSG_FILE_DEFINITION_ERROR, ERROR, OK
from .interface_file_util import check_file_and_interface_type
from .models import Contract, InterfaceCall
from django.db.utils import IntegrityError

from .interface_file import check_file_is_excel_file, check_file_has_excel_extension, is_valid_header_row, \
    get_mandatory_field_positions, get_headers_from_sheet, get_fields_with_their_position, mandatory_fields_present
from .negometrix import register_contract, NegometrixInterfaceFile


class ContractTest(TestCase):

    def setUp(self):
        self.interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                          status='TestStatus',
                                                          filename='Text.xls',
                                                          system='TestSysteem')
        self.contract_1 = Contract.objects.create(contract_nr='NL-123',
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
        self.assertEqual(self.contract_1.__str__(), expected)

    def test_one_interface_call_on_page(self):
        response = self.client.get('/interfacecalls')
        self.assertContains(response, 'TestStatus')
        self.assertContains(response, 'TestSysteem')

    def test_one_contract_on_interface_call_page(self):
        response = self.client.get(f'/interfacecall/{self.interfaceCall.pk}/')
        self.assertContains(response, 'NL-123')
        self.assertContains(response, 'Test Contract')
        self.assertContains(response, 'T. Ester')

    def test_two_contract_on_interface_call_page(self):
        Contract.objects.create(contract_nr='NL-345',
                                seq_nr=1,
                                description='Test Contract 2',
                                contract_owner='T. Ester',
                                interface_call=self.interfaceCall)
        response = self.client.get(f'/interfacecall/{self.interfaceCall.pk}/')
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
        try:
            check_file_has_excel_extension(filename)
        except Exception as ex:
            self.assertTrue("Bestand heeft geen excel extensie" in ex.__str__())

    def test_an_excel_file_extension_xls(self):
        filename = 'test.xls'
        self.assertTrue(check_file_has_excel_extension(filename))

    def test_an_excel_file_extension_XLS(self):
        filename = 'test.XLS'
        self.assertTrue(check_file_has_excel_extension(filename))

    def test_an_excel_file_extension_xlsx(self):
        filename = 'test.xlsx'
        self.assertTrue(check_file_has_excel_extension(filename))

    def test_an_excel_file_extension_XLSX(self):
        filename = 'test.XLSX'
        self.assertTrue(check_file_has_excel_extension(filename))

    # Test on really being an Excel file, so can it be read as Workbook?

    def test_not_an_excelfile(self):
        file = open("rm/test/resources/aPdfWithExcelExtension.xls", "rb")
        print(f'type of file: {type(file)}')
        try:
            is_excel = check_file_is_excel_file(file)
        except Exception as ex:
            self.assertTrue("Het openen van dit bestand als excel bestand"
                            " geeft een foutmelding" in ex.__str__())

    def test_an_excelfile_xlsx(self):
        file = open("rm/test/resources/a_valid_excel_file.xlsx", "rb")
        print(f'type of file: {type(file)}')
        is_excel = check_file_is_excel_file(file)
        self.assertTrue(is_excel)

    # Test valid headers

    def test_valid_header_row_exact(self):
        self.assertTrue(is_valid_header_row(found_headers=('x', 'y', 'z'),
                                            mandatory_headers=('x', 'z')))

    def test_valid_header_row_case_sensitive(self):
        self.assertTrue(is_valid_header_row(found_headers=('X', 'y', 'z'),
                                            mandatory_headers=('x', 'z')))

    def test_invalid_header_row(self):
        self.assertFalse(is_valid_header_row(found_headers=('a', 'b', 'z'),
                                             mandatory_headers=('x', 'z')))

    # Test handle uploaded excel file

    def test_check_excel_file_invalid_headers(self):
        try:
            interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                         status='TestStatus',
                                                         filename='valid_excel_without_headers.xlsx')
            file = "rm/test/resources/valid_excel_without_headers.xlsx"
            check_file_and_interface_type(file, interfaceCall)
        except Exception as ex:
            self.assertTrue("File can not be recognized" in ex.__str__(),
                            f"We got another exception than expected, received: {ex.__str__()}")
        else:
            self.assertTrue(False, "No Exception, while expected because file has no headers")

    def test_check_valid_negometrix_excel_file(self):
        interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                     status='TestStatus',
                                                     filename='test_register_contract.xlsx')
        file = "rm/test/resources/test_register_contract.xlsx"
        excelInterfaceFile = check_file_and_interface_type(file, interfaceCall)
        self.assertTrue(isinstance(excelInterfaceFile, NegometrixInterfaceFile))

    def test_upload_valid_negometrix_excel_file_2_valid_rows(self):
        interfaceCall = InterfaceCall.objects.create(
            date_time_creation=Now(),
            status='TestStatus',
            filename='test_upload_valid_negometrix_excel_file_2_valid_rows.xlsx')
        file = "rm/test/resources/test_upload_valid_negometrix_excel_file_2_valid_rows.xlsx"
        excelInterfaceFile = check_file_and_interface_type(file, interfaceCall)
        self.assertTrue(isinstance(excelInterfaceFile, NegometrixInterfaceFile))

        excelInterfaceFile.process()

        contracten = interfaceCall.contracten.all()
        self.assertEqual(len(contracten),2)

        contract1 = contracten[0]
        self.assertEqual(contract1.contract_nr, '44335')
        contract2 = contracten[1]
        self.assertEqual(contract2.contract_nr, '44336')

        received_data = interfaceCall.received_data.all()
        self.assertEqual(len(received_data),3)


    def test_upload_valid_negometrix_excel_file_2_valid_rows_1_invalid_row(self):
        interfaceCall = InterfaceCall.objects.create(
            date_time_creation=Now(),
            status='TestStatus',
            filename='test_upload_valid_negometrix_excel_file_2_valid_rows_1_invalid_row.xlsx')
        file = "rm/test/resources/test_upload_valid_negometrix_excel_file_2_valid_rows_1_invalid_row.xlsx"
        excelInterfaceFile = check_file_and_interface_type(file, interfaceCall)
        self.assertTrue(isinstance(excelInterfaceFile, NegometrixInterfaceFile))

        excelInterfaceFile.process()

        contracten = interfaceCall.contracten.all()
        self.assertEqual(len(contracten),2)

        contract1 = contracten[0]
        self.assertEqual(contract1.contract_nr, '44335')
        contract2 = contracten[1]
        self.assertEqual(contract2.contract_nr, '44337')

        received_data = interfaceCall.received_data.all()
        self.assertEqual(len(received_data),4)
        self.assertEqual(received_data[0].status, OK)
        self.assertEqual(received_data[1].status, OK)
        self.assertEqual(received_data[2].status, ERROR)
        self.assertEqual(received_data[3].status, OK)

    #  Test generic database functions

    def test_get_field_positions(self):

        found_headers = ['Header 1', "just a field", 'Header x', 'and another']
        defined_headers = dict(
            header_01="Header 1",
            zomaarwat="something",
            header_x="Header x",
        )
        field_positions = get_fields_with_their_position(found_headers,
                                                         defined_headers)

        expected_field_opsitions = dict(
            header_01=0,
            header_x=2,
        )
        self.assertEqual(len(field_positions), 2)
        self.assertEqual(field_positions, expected_field_opsitions)

    def test_get_mandatory_field_positions_valid_situation(self):
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
        mandatory_field_positions = [2, 3]
        row_values = ["nul", "een", "twee", None, "vier"]
        self.assertFalse(mandatory_fields_present(mandatory_field_positions,
                                                  row_values))

    def test_get_headers(self):
        file = open("rm/test/resources/test_get_headers.xlsx", "rb")
        workbook: Workbook = load_workbook(file)
        sheet = workbook.active
        headers = get_headers_from_sheet(sheet)
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
            count += 1

        interfaceCall = InterfaceCall.objects.create(date_time_creation=Now(),
                                                     status='TestStatus',
                                                     filename='test_register_contract.xlsx')

        fields_with_position = dict(database_nr=0,
                                    contract_nr=1,
                                    contract_status=2,
                                    description=3,
                                    )

        mandatory_field_positions = (1, 2)
        mandatory_fields = ('a_field', 'another_field')

        status, msg = register_contract(row_nr, values_row_4, interfaceCall, fields_with_position,
                                        mandatory_field_positions)

        expected_status = ERROR

        self.assertEqual(status, expected_status)

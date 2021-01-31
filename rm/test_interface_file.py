from django.db.models.functions import Now
from django.test import TestCase
from openpyxl import Workbook, load_workbook

from rm.constants import RowStatus, ERROR_MSG_FILE_DEFINITION_ERROR
from rm.interface_file import RowStatistics, check_file_has_excel_extension, check_file_is_excel_file, \
    is_valid_header_row, get_fields_with_their_position, get_mandatory_field_positions, mandatory_fields_present, \
    get_headers_from_sheet
from rm.interface_file_util import check_file_and_interface_type
from rm.models import InterfaceCall
from rm.test_util import setUpUser
from rm.views import process_file


class RowStatisticTests(TestCase):

    def test_one_empty_row(self):
        row_statistics = RowStatistics()
        row_statistics.add_row_with_status(RowStatus.EMPTY_ROW)
        self.assertEqual(row_statistics.get_total_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_rows_received(), 0)
        self.assertEqual(row_statistics.get_total_data_error_rows(), 0)
        self.assertEqual(row_statistics.get_total_header_rows(), 0)
        self.assertEqual(row_statistics.get_total_empty_rows(), 1)

    def test_one_header_row(self):
        row_statistics = RowStatistics()
        row_statistics.add_row_with_status(RowStatus.HEADER_ROW)
        self.assertEqual(row_statistics.get_total_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_rows_received(), 0)
        self.assertEqual(row_statistics.get_total_data_error_rows(), 0)
        self.assertEqual(row_statistics.get_total_header_rows(), 1)

    def test_one_data_ok_row(self):
        row_statistics = RowStatistics()
        row_statistics.add_row_with_status(RowStatus.DATA_OK)
        self.assertEqual(row_statistics.get_total_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_rows_received(), 1)

    def test_one_data_error_row(self):
        row_statistics = RowStatistics()
        row_statistics.add_row_with_status(RowStatus.DATA_ERROR)
        self.assertEqual(row_statistics.get_total_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_error_rows(), 1)

    def test_one_data_warning_row(self):
        row_statistics = RowStatistics()
        row_statistics.add_row_with_status(RowStatus.DATA_WARNING)
        self.assertEqual(row_statistics.get_total_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_error_rows(), 0)
        self.assertEqual(row_statistics.get_total_data_warning_rows(), 1)

    def test_one_data_ignored_row(self):
        row_statistics = RowStatistics()
        row_statistics.add_row_with_status(RowStatus.DATA_IGNORED)
        self.assertEqual(row_statistics.get_total_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_rows_received(), 1)
        self.assertEqual(row_statistics.get_total_data_error_rows(), 0)
        self.assertEqual(row_statistics.get_total_data_warning_rows(), 0)
        self.assertEqual(row_statistics.get_total_data_ignored_rows(), 1)

    def test_all_types(self):
        row_statistics = RowStatistics()
        row_statistics.add_row_with_status(RowStatus.EMPTY_ROW)
        row_statistics.add_row_with_status(RowStatus.HEADER_ROW)
        row_statistics.add_row_with_status(RowStatus.DATA_OK)
        row_statistics.add_row_with_status(RowStatus.DATA_ERROR)
        row_statistics.add_row_with_status(RowStatus.DATA_WARNING)
        row_statistics.add_row_with_status(RowStatus.DATA_IGNORED)
        self.assertEqual(row_statistics.get_total_rows_received(), 6)
        self.assertEqual(row_statistics.get_total_data_rows_received(), 4)
        self.assertEqual(row_statistics.get_total_data_ok_rows(), 1)
        self.assertEqual(row_statistics.get_total_data_error_rows(), 1)
        self.assertEqual(row_statistics.get_total_data_warning_rows(), 1)
        self.assertEqual(row_statistics.get_total_data_ignored_rows(), 1)

    def test_all_types_as_string(self):
        row_statistics = RowStatistics()
        row_statistics.add_row_with_status(RowStatus.EMPTY_ROW.name)
        row_statistics.add_row_with_status(RowStatus.HEADER_ROW.name)
        row_statistics.add_row_with_status(RowStatus.DATA_OK.name)
        row_statistics.add_row_with_status(RowStatus.DATA_ERROR.name)
        row_statistics.add_row_with_status(RowStatus.DATA_WARNING.name)
        row_statistics.add_row_with_status(RowStatus.DATA_IGNORED.name)
        self.assertEqual(row_statistics.get_total_rows_received(), 6)
        self.assertEqual(row_statistics.get_total_data_rows_received(), 4)
        self.assertEqual(row_statistics.get_total_data_ok_rows(), 1)
        self.assertEqual(row_statistics.get_total_data_error_rows(), 1)
        self.assertEqual(row_statistics.get_total_data_warning_rows(), 1)
        self.assertEqual(row_statistics.get_total_data_ignored_rows(), 1)


class ExtentionTests(TestCase):

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


class FileFormatTests(TestCase):
    """
    Test if the file is an Excel file, so can it be read as Workbook?
    """

    def test_empty_file_with_xls_extension(self):
        file = open("rm/test/resources/EmptyFileWithXLSExtension.xls", "rb")
        print(f'type of file: {type(file)}')
        try:
            is_excel = check_file_is_excel_file(file)
        except Exception as ex:
            self.assertTrue("Het openen van dit bestand als excel bestand"
                            " geeft een foutmelding" in ex.__str__())

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


class GenericHeaderTests(TestCase):
    """
    Test valid headers
    """

    def test_valid_header_row_exact(self):
        self.assertTrue(is_valid_header_row(found_headers=('x', 'y', 'z'),
                                            mandatory_headers=('x', 'z')))

    def test_valid_header_row_case_sensitive(self):
        self.assertTrue(is_valid_header_row(found_headers=('X', 'y', 'z'),
                                            mandatory_headers=('x', 'z')))

    def test_invalid_header_row(self):
        self.assertFalse(is_valid_header_row(found_headers=('a', 'b', 'z'),
                                             mandatory_headers=('x', 'z')))

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


class FieldPositionsTests(TestCase):

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
        mandatory_field_positions = (2, 3)
        row_values = ("nul", "een", "twee", "drie", "vier")
        self.assertTrue(mandatory_fields_present(mandatory_field_positions,
                                                 row_values))

    def test_mandatory_fields_not_present_1_pos_empty_string(self):
        mandatory_field_positions = (3, )
        row_values = ("nul", "een", "twee", "", "vier")
        self.assertFalse(mandatory_fields_present(mandatory_field_positions,
                                                  row_values))

    def test_mandatory_fields_not_present_1_ok_1_not_and_none(self):
        mandatory_field_positions = [2, 3]
        row_values = ["nul", "een", "twee", None, "vier"]
        self.assertFalse(mandatory_fields_present(mandatory_field_positions,
                                                  row_values))


class GenericExcelTests(TestCase):
    def test_get_headers(self):
        file = open("rm/test/resources/test_get_headers.xlsx", "rb")
        workbook: Workbook = load_workbook(file)
        sheet = workbook.active
        headers = get_headers_from_sheet(sheet)
        expected = ("HEADER 1", "HEADER 2", None, "HEADER 4")
        self.assertEqual(headers, expected)

    def test_check_excel_file_invalid_headers(self):
        try:
            interface_call = InterfaceCall.objects.create(date_time_creation=Now(),
                                                          status='TestStatus',
                                                          filename='valid_excel_without_headers.xlsx')
            file = "rm/test/resources/valid_excel_without_headers.xlsx"
            check_file_and_interface_type(file)
        except Exception as ex:
            self.assertTrue("File can not be recognized" in ex.__str__(),
                            f"We got another exception than expected, received: {ex.__str__()}")
        else:
            self.assertTrue(False, "No Exception, while expected because file has no headers")


class GenericFileUploadTests(TestCase):

    def setUp(self):
        setUpUser(self, superuser=True)

    def test_upload_empty_file_with_xls(self):
        nr_int_calls_before = len(InterfaceCall.objects.all())
        file = open("rm/test/resources/EmptyFileWithXLSExtension.xls", "rb")
        status, msg = process_file(file, self.user)
        nr_int_calls_after = len(InterfaceCall.objects.all())
        self.assertEqual(nr_int_calls_after, nr_int_calls_before + 1)

        interface_call: InterfaceCall = InterfaceCall.objects.last()
        self.assertEqual(interface_call.filename, "rm/test/resources/EmptyFileWithXLSExtension.xls")
        self.assertTrue(interface_call.message.__contains__('Het openen van dit bestand als excel bestand '
                                                            'geeft een foutmelding: File is not a zip file'))
from django.contrib.auth import get_user_model
from django.db.models.functions import Now
from django.test import TestCase

from rm.constants import RowStatus
from rm.interface_file import RowStatistics


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



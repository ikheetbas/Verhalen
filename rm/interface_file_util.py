from django.db.models.functions import Now
from openpyxl import load_workbook

from rm.constants import NEW, INTERFACE_TYPE_FILE, ERROR_MSG_FILE_CAN_NOT_BE_RECOGNISED
from rm.interface_file import ExcelInterfaceFile, check_file_has_excel_extension, check_file_is_excel_file, get_headers_from_sheet, \
    is_valid_header_row, ExcelInterfaceFile, get_headers_from_file
from rm.models import InterfaceCall
from rm.negometrix import NegometrixInterfaceFile


def check_file_and_interface_type(file, interfaceCall: InterfaceCall) -> ExcelInterfaceFile:
    """
    Checks what type of Interface the file is, performs checks and returns
    the right subclass of ExcelInterfaceFile:
    - NegometrixFile
    -
    """

    check_file_has_excel_extension(file if type(file) == str else file.name)

    check_file_is_excel_file(file)

    headers_in_file = get_headers_from_file(file)

    # TODO later build something nice and flexible for multipe interface files, now we
    #  hardcoded check on Negometrix headers
    if is_valid_header_row(headers_in_file,
                           NegometrixInterfaceFile.mandatory_headers):
        return NegometrixInterfaceFile(file, interfaceCall)
    else:
        raise Exception(ERROR_MSG_FILE_CAN_NOT_BE_RECOGNISED)
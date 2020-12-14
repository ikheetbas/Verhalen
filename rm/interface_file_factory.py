from django.db.models.functions import Now
from openpyxl import load_workbook

from rm.constants import NEW, INTERFACE_TYPE_FILE, ERROR_MSG_FILE_CAN_NOT_BE_RECOGNISED
from rm.interface_file import ExcelInterfaceFile, file_has_excel_extension, file_is_excel_file, get_headers_from_sheet, \
    is_valid_header_row, ExcelInterfaceFile, get_headers_from_file
from rm.models import InterfaceCall
from rm.negometrix import NegometrixInterfaceFile


def interfaceFileFactory(file, interfaceCall: InterfaceCall) -> ExcelInterfaceFile:
    """
    Checks what type of Interface the file is, performs checks and returns
    the right subtype of InterfaceFile:
    - NegometrixFile
    -
    """

    has_excel_extension, message = file_has_excel_extension(file if type(file) == str else file.name)
    if not has_excel_extension:
        raise Exception(message)

    is_excel, message = file_is_excel_file(file)
    if not is_excel:
        raise Exception(message)

    available_headers = get_headers_from_file(file)

    if is_valid_header_row(available_headers, NegometrixInterfaceFile.mandatory_headers):
        return NegometrixInterfaceFile(file, interfaceCall)

    raise Exception(ERROR_MSG_FILE_CAN_NOT_BE_RECOGNISED)
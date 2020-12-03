import pathlib
import logging

from django.core.files.uploadedfile import UploadedFile
from django.db.models.functions import Now
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from rm.forms import UploadFileForm
from rm.models import Contract, InterfaceCall
from rm.negometrix import required_headers

logger = logging.getLogger(__name__)


def file_has_excel_extension(filename: str) -> [bool, str]:
    extension = pathlib.Path(filename).suffix.upper()
    if not extension in ['.XLS', '.XLSX']:
        return [ False ,
                 f"Bestand heeft geen excel extensie maar: '{extension}'"]
    else:
        return [ True, "OK"]


def file_is_excel_file(file: UploadedFile) -> [bool, str]:
    try:
        load_workbook(filename=file)
    except Exception as ex:
        return [ False , f"Het openen van dit bestand als excel bestand"
                         f" geeft een foutmelding: {ex.__str__()}"]
    return [True, "OK"]


def get_headers(sheet: Worksheet) -> ['str']:
    headers = []
    for value in sheet.iter_rows(min_row=1,
                                  max_row=1,
                                  values_only=True):
        headers.append(value)
    return headers


def is_valid_header_row(headers: [str], required_headers: [str]) -> bool:
    headers_upper = [x.upper() for x in headers]
    required_headers_upper = [x.upper() for x in required_headers]
    valid = all(item in headers_upper for item in required_headers_upper)
    return valid


def handle_uploaded_excel_file(excelfile):
    workbook = load_workbook(filename=excelfile)
    sheet = workbook.active
    headers = get_headers(sheet)
    if is_valid_header_row(headers, required_headers):
        raise Exception(f"File {excelfile.name} has no (valid) header row, missing one of {required_headers}")


def handle_uploaded_file(file):
    has_excel_extension, msg = file_has_excel_extension(file.name)
    if not has_excel_extension:
        return [False, msg]

    is_excel, message = file_is_excel_file(file)
    if not is_excel:
        raise Exception(message)
    
    # register file in InterfaceCall
    interfaceCall = InterfaceCall.objects.create(filename=file.name,
                                                 status='New',
                                                 date_time_creation=Now(),
                                                 type="FILE-UPLOAD")
    try:
        handle_uploaded_excel_file(file)
        interfaceCall.status='Ready'
    except Exception as ex:
        interfaceCall.status='Error'
        interfaceCall.message=f'Reason: {ex.__str__()}'

    interfaceCall.save()


def upload_file(request):
    print('in upload_file')
    if request.method == 'POST':
        print('in upload_file.. POST')
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print('in upload_file.. form is valid')
            try:
                file = request.FILES['file']
                logger.warning(f"Type of file {type(file)}")
                handle_uploaded_file(file)
            except Exception as ex:
                form.add_error("file", ex.__str__())
                return render(request, 'rm/upload.html', {'form': form})
            return HttpResponseRedirect('/rm/')
        else:
            print('in upload_file.. form not valid')
    else:
        print('in upload_file.. <>POST')
        form = UploadFileForm()
    return render(request, 'rm/upload.html', {'form': form})


class ContractListView(ListView):
    model = Contract
    context_object_name = 'contract_list'
    template_name = 'rm/contract_list.html'

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

from rm.files import create

logger = logging.getLogger(__name__)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = request.FILES['file']
                logger.debug(f"Type of file {type(file)}")
                interfaceFile = create(file)
                logger.debug(f"Type of rm.file {type(interfaceFile)}")
                interfaceFile.process()
            except Exception as ex:
                form.add_error("file", ex.__str__())
                return render(request, 'upload.html', {'form': form})
            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


class ContractListView(ListView):
    model = Contract
    context_object_name = 'contract_list'
    template_name = 'contract_list.html'

import logging

from django.db.models.functions import Now
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.generic import ListView

from rm.constants import INTERFACE_TYPE_FILE, NEW, UNKNOWN, ERROR
from rm.forms import UploadFileForm
from rm.models import Contract, InterfaceCall
from rm.interface_file_util import check_file_and_interface_type

logger = logging.getLogger(__name__)


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            # First things first, register file in InterfaceCall
            interfaceCall = InterfaceCall.objects.create(filename=file.name,
                                                         status=NEW,
                                                         date_time_creation=Now(),
                                                         type=INTERFACE_TYPE_FILE,
                                                         system=UNKNOWN)
            try:
                # check the file and try to find out what type it is
                interfaceFile = check_file_and_interface_type(file, interfaceCall)

                # register found system in the interfaceFile registration
                system = interfaceFile.get_interface_system()
                interfaceCall.system = system
                interfaceCall.save()

                # process the file!
                interfaceFile.process()

            except Exception as ex:

                interfaceCall.status=ERROR
                interfaceCall.message=ex.__str__()
                interfaceCall.save()

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

class InterfaceCallListView(ListView):
    model = InterfaceCall
    context_object_name = 'interface_call_list'
    template_name = 'interface_call_list.html'
    ordering = ['-date_time_creation']


def interface_call_contracts(request, pk: int):
    logger.debug(f"interface_call_contracts: pk: {pk}")
    interfaceCall = InterfaceCall.objects.get(pk=pk)
    logger.debug("interfaceCall: " + interfaceCall.__str__())
    contracts = interfaceCall.contracten.all()
    context = {
        'interface_call': interfaceCall,
        'contract_list': contracts
    }
    template = loader.get_template('interface_call_contract_list.html')
    return HttpResponse(template.render(context, request))

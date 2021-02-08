import logging

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Now
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views import View
from django.views.generic import ListView, TemplateView

from rm.constants import FileStatus
from rm.forms import UploadFileForm
from rm.models import InterfaceCall, DataPerOrgUnit
from rm.interface_file_util import check_file_and_interface_type
from rm.view_util import get_datasets_for_user

logger = logging.getLogger(__name__)


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


def process_file(file, user):
    """
    Process the file, register it with the user, find out the type

    """
    # First things first, create the InterfaceCall, with the user
    interface_call = InterfaceCall(filename=file.name,
                                   status=FileStatus.NEW,
                                   date_time_creation=Now(),
                                   user=user,
                                   username=user.username,
                                   user_email=user.email)
    try:
        # check the file and try to find out what type it is
        interface_file = check_file_and_interface_type(file)

        # register InterfaceDefinition
        interface_call.interface_definition = interface_file.get_interface_definition()
        interface_call.save()

        # process the file!
        interface_file.process(interface_call)

    except Exception as ex:

        interface_call.status = FileStatus.ERROR.name
        interface_call.message = ex.__str__()
        interface_call.save()
        return "ERROR", ex.__str__()

    return "OK", "File has been processed"


@permission_required('rm.upload_contract_file', raise_exception=True)
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            status, msg = process_file(file, request.user)

            if status == "ERROR":
                form.add_error("file", msg)
                return render(request, 'rm/upload.html', {'form': form})
            else:
                return HttpResponseRedirect('/interfacecalls')
    else:
        form = UploadFileForm()
    return render(request, 'rm/upload.html', {'form': form})


class InterfaceCallListView(ListView):
    model = InterfaceCall
    context_object_name = 'interface_call_list'
    template_name = 'rm/interface_call_list.html'
    # ordering = ['-date_time_creation'] is done through DataTables in JavaScript (see custom.css)


@permission_required('rm.view_contract', raise_exception=True)
def interface_call_details(request, pk: int):
    logger.debug(f"interface_call_details: pk: {pk}")
    interface_call = InterfaceCall.objects.get(pk=pk)
    logger.debug("interface_call: " + interface_call.__str__())

    stage_contracts = interface_call.stage_contracts()

    raw_data = interface_call.rawdata_set.all()
    context = {
        'interface_call': interface_call,
        'stage_contract_list': stage_contracts,
        'received_data': raw_data,
    }
    template = loader.get_template('rm/interface_call_details.html')
    return HttpResponse(template.render(context, request))


class DataSetListView(ListView):
    context_object_name = 'dataset_list'
    template_name = 'rm/dataset_list.html'

    def get_queryset(self):
        params = self.request.GET
        queryset = get_datasets_for_user(self.request.user, params)

        result = []
        for dpou in queryset:
            record = {"system": dpou.interface_call.interface_definition.system.name,
                      "dataset_type": dpou.interface_call.interface_definition.data_set_type.name,
                      "interface_type": dpou.interface_call.interface_definition.get_interface_type_display(),
                      "status": dpou.active,
                      "date_time": dpou.interface_call.date_time_creation,
                      "org_unit": dpou.org_unit.name,
                      "data_rows_ok": dpou.number_of_data_rows_ok,
                      "data_rows_warning": dpou.number_of_data_rows_warning
                      }
            result.append(record)
        return result


class RefreshDataSets(View):
    pass

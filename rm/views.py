import logging

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.functions import Now
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.generic import ListView, TemplateView, DetailView

from rm.constants import FileStatus
from rm.forms import UploadFileForm
from rm.models import InterfaceCall
from rm.interface_file_util import check_file_and_interface_type
from rm.view_util import get_datasets_for_user, get_active_datasets_per_interface_for_users_org_units

logger = logging.getLogger(__name__)


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'




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


def create_contracten_interface_context(pk):
    logger.debug(f"interface_call_details: pk: {pk}")
    interface_call = InterfaceCall.objects.get(pk=pk)
    logger.debug("interface_call: " + interface_call.__str__())

    stage_contracts_dict = interface_call.stage_contracts_per_org()

    raw_data = interface_call.rawdata_set.all()
    context = {
        'interface_call': interface_call,
        'stage_contract_dict': stage_contracts_dict,
        'received_data': raw_data,
    }
    return context


@permission_required('rm.view_contract', raise_exception=True)
def interface_call_details(request, pk: int):
    logger.debug(f"interface_call_details: pk: {pk}")
    interface_call = InterfaceCall.objects.get(pk=pk)
    logger.debug("interface_call: " + interface_call.__str__())

    stage_contracts_list = interface_call.stage_contracts()

    raw_data = interface_call.rawdata_set.all()
    context = {
        'interface_call': interface_call,
        'stage_contract_list': stage_contracts_list,
        'received_data': raw_data,
    }
    template = loader.get_template('rm/interface_call_details.html')
    return HttpResponse(template.render(context, request))


class DataSetListView(ListView):
    context_object_name = 'dataset_list'
    template_name = 'rm/dataset_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.debug(f"get_context_data {self.request.GET} ")
        params = self.request.GET

        active = params.get('active', 'True')
        dataset_type = params.get('dataset_type_contracten', 'All')
        my_datasets = params.get('my_datasets', 'False')

        context["active"] = active
        context["dataset"] = dataset_type
        context["my_datasets"] = my_datasets

        return context

    def get_queryset(self):
        logger.debug("get_queryset")
        params = self.request.GET
        queryset = get_datasets_for_user(self.request.user, params)

        datasets = []
        for dpou in queryset:
            record = {"system": dpou.interface_call.interface_definition.system.name,
                      "dataset_type": dpou.interface_call.interface_definition.data_set_type.name,
                      "interface_type": dpou.interface_call.interface_definition.get_interface_type_display(),
                      "status": "Actief" if dpou.active else "Inactief",
                      "username": dpou.interface_call.username,
                      "date_time": dpou.interface_call.date_time_creation,
                      "org_unit": dpou.org_unit.name,
                      "data_rows_ok": dpou.number_of_data_rows_ok if dpou.number_of_data_rows_ok > 0 else "",
                      "data_rows_warning": dpou.number_of_data_rows_warning if dpou.number_of_data_rows_warning > 0 else "",
                      }
            datasets.append(record)
        return datasets


class InterfaceListView(ListView):
    context_object_name = 'interface_list'
    template_name = 'rm/interface_list.html'

    def get_queryset(self):
        rows = get_active_datasets_per_interface_for_users_org_units(self.request.user)
        return rows


def handle_uploaded_file(param):
    pass

@permission_required("rm.contracten_upload", raise_exception=True)
def contracten_upload(request, pk):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            call_id, status, msg = process_file(file, request.user)

            return HttpResponseRedirect(f'/interfacecalls/{call_id}')
    else:
        form = UploadFileForm()

    return render(request, 'rm/contracten_upload.html', {'form': form})


class ContractenUploadView(PermissionRequiredMixin, TemplateView):
    model = InterfaceCall
    permission_required = "rm.contracten_upload"
    context_object_name = 'interface_list'
    template_name = 'rm/contracten_upload.html'
    form_class = UploadFileForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            call_id, status, msg = process_file(file, request.user)

            return HttpResponseRedirect(f'/contracten_upload/{call_id}')

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        form = self.form_class()
        context = {'form': form}
        if pk:
            context = {**context, **create_contracten_interface_context(pk)}
        return render(request, self.template_name, context)

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

        # register InterfaceDefinition (System & DataSetType)
        interface_call.interface_definition = interface_file.get_interface_definition()
        interface_call.save()

        # process the file!
        interface_file.process(interface_call)

    except Exception as ex:

        interface_call.status = FileStatus.ERROR.name
        interface_call.message = ex.__str__()
        interface_call.save()
        return interface_call.id, "ERROR", ex.__str__()

    return interface_call.id, "OK", "File has been processed"

import logging

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.views.generic import ListView, TemplateView

from rm.constants import NEGOMETRIX, CONTRACTEN
from rm.forms import UploadFileForm, DatasetForm
from rm.models import InterfaceCall, DataPerOrgUnit
from rm.view_util import get_datasets_for_user, get_active_datasets_per_interface_for_users_org_units, process_file
from users.models import CustomUser

logger = logging.getLogger(__name__)


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'



class UploadsListView(ListView):
    model = InterfaceCall
    context_object_name = 'uploads_list'
    template_name = 'rm/uploads_list.html'
    # ordering = ['-date_time_creation'] is done through DataTables in JavaScript (see custom.css)


def create_contracten_interface_context(pk):
    logger.debug(f"interface_call_details: pk: {pk}")
    interface_call = InterfaceCall.objects.get(pk=pk)
    logger.debug("interface_call: " + interface_call.__str__())

    stage_contracts_dict = interface_call.stage_contracts_per_org()

    raw_data = interface_call.rawdata_set.all().order_by("seq_nr")
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


def get_dataset_details_url(dataset_type_name: str, user: CustomUser, id) -> str:
    """
    Depending the permission and dataset type this returns a string with the url or not.
    It would be nice to make this more generic, but for the moment it's hard coded.
    And since the screens differ per dataset_type as well it's not that big issue.
    """
    if dataset_type_name.lower() == CONTRACTEN.lower() and user.has_perm("rm.view_contract"):
        return f"/contracten_dataset_details/{id}"
    return None

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

            details_url = get_dataset_details_url(dataset_type_name=dpou.interface_call.interface_definition.data_set_type.name,
                                                  user=self.request.user,
                                                  id=dpou.id)
            logger.debug(f"details_url = {details_url}")

            record = {"id": dpou.id,
                      "system": dpou.interface_call.interface_definition.system.name,
                      "dataset_type": dpou.interface_call.interface_definition.data_set_type.name,
                      "interface_type": dpou.interface_call.interface_definition.get_interface_type_display(),
                      "status": "Actief" if dpou.active else "Inactief",
                      "username": dpou.interface_call.username,
                      "date_time": dpou.interface_call.date_time_creation,
                      "org_unit": dpou.org_unit.name,
                      "data_rows_ok": dpou.number_of_data_rows_ok if dpou.number_of_data_rows_ok > 0 else "",
                      "data_rows_warning": dpou.number_of_data_rows_warning if dpou.number_of_data_rows_warning > 0 else "",
                      "details_url": details_url
                      }
            datasets.append(record)
        return datasets


class InterfaceListView(ListView):
    context_object_name = 'interface_list'
    template_name = 'rm/interface_list.html'

    def get_queryset(self):
        rows = get_active_datasets_per_interface_for_users_org_units(self.request.user)
        return rows




class ContractenUploadView(PermissionRequiredMixin, TemplateView):
    model = InterfaceCall
    permission_required = "rm.contracten_upload"
    context_object_name = 'interface_list'
    template_name = 'rm/contracten_upload.html'
    form_class = UploadFileForm

    def post(self, request, *args, **kwargs):
        logger.debug("POST")
        if request.POST.get("activate"):
            call_id = request.POST.get("interface_call_id")
            call = InterfaceCall.objects.get(pk=int(call_id))
            call.activate_interface_call(start_transaction=True, cascading=True)
            logger.debug(f"Call: {call_id} activated")
            return HttpResponseRedirect(f'/contracten_upload/{call_id}')
        else:
            logger.debug("Upload contracten file")
            form: UploadFileForm = self.form_class(request.POST, request.FILES)
            logger.debug(f"Upload contracten file, form: {form}")
            if form.is_valid():
                logger.debug("Upload contracten file, form.is.valid()")
                file = request.FILES['file']
                logger.debug(f"Upload contracten file, file = {file}")
                call_id, status, msg = process_file(file=file,
                                                    user=request.user,
                                                    expected_system=NEGOMETRIX)
                return HttpResponseRedirect(f'/contracten_upload/{call_id}')
            else:
                logger.debug("Upload contracten file, not form.is.valid()")
                return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        form = self.form_class()
        context = {'form': form}
        if pk:
            context = {**context, **create_contracten_interface_context(pk)}
        return render(request, self.template_name, context)


class ContractenUploadDetailsView(PermissionRequiredMixin, TemplateView):
    model = InterfaceCall
    permission_required = "rm.view_contract"
    context_object_name = 'interface_list'
    template_name = 'rm/contracten_upload_details.html'
    form_class = UploadFileForm

    def post(self, request, *args, **kwargs):
        logger.debug("POST")
        if request.POST.get("activate"):
            call_id = request.POST.get("interface_call_id")
            call = InterfaceCall.objects.get(pk=int(call_id))
            call.activate_interface_call(start_transaction=True, cascading=True)
            logger.debug(f"Call: {call_id} activated")
            return HttpResponseRedirect(f'/contracten_upload_details/{call_id}')
        if request.POST.get("deactivate"):
            call_id = request.POST.get("interface_call_id")
            call = InterfaceCall.objects.get(pk=int(call_id))
            call.deactivate_interface_call(start_transaction=True)
            logger.debug(f"Call: {call_id} deactivated")
            return HttpResponseRedirect(f'/contracten_upload_details/{call_id}')
        return render(request, reverse("contracten_dataset_details"))

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        form = self.form_class()
        context = {'form': form}
        if pk:
            context = {**context, **create_contracten_interface_context(pk)}
        return render(request, self.template_name, context)


def create_contracten_dataset_context(pk):
    dpou = DataPerOrgUnit.objects.get(pk=pk)
    stage_contracts_list = dpou.stagecontract_set.all().order_by("seq_nr")
    raw_data = dpou.interface_call.rawdata_set.all().order_by("seq_nr")
    context = {
        'dpou': dpou,
        'stage_contract_list': stage_contracts_list,
        'raw_data': raw_data,
    }
    return context


class ContractenDatasetDetailsView(PermissionRequiredMixin, TemplateView):
    model = DataPerOrgUnit
    permission_required = "rm.view_contract"
    context_object_name = 'dataset'
    template_name = 'rm/contracten_dataset_details.html'
    form_class = DatasetForm

    def post(self, request, *args, **kwargs):
        logger.debug("POST")
        if request.POST.get("activate"):
            dpou_id = request.POST.get("dpou_id")
            dpou = DataPerOrgUnit.objects.get(pk=int(dpou_id))
            dpou.activate_dataset(start_transaction=True)
            logger.debug(f"DPOU: {dpou_id} activated")
            return HttpResponseRedirect(f'/contracten_dataset_details/{dpou_id}')
        if request.POST.get("deactivate"):
            dpou_id = request.POST.get("dpou_id")
            dpou = DataPerOrgUnit.objects.get(pk=int(dpou_id))
            dpou.deactivate_dataset(start_transaction=True)
            logger.debug(f"DPOU: {dpou_id} deactivated")
            return HttpResponseRedirect(f'/contracten_dataset_details/{dpou_id}')
        return render(request, reverse("contracten_dataset_details"))

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        form = self.form_class()
        context = {'form': form}
        if pk:
            context = {**context, **create_contracten_dataset_context(pk)}
        return render(request, self.template_name, context)


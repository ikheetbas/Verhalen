import logging

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse
from django.views.generic import ListView, TemplateView, DetailView

from rm.constants import NEGOMETRIX, CONTRACTEN, UNKNOWN
from rm.forms import UploadFileForm, DatasetForm
from rm.models import InterfaceCall, DataPerOrgUnit
from rm.view_util import set_session_timeout_inactivity, get_minutes_timeout, get_datasets_for_user, \
    get_active_datasets_per_interface_for_users_org_units, process_file
from users.models import CustomUser

logger = logging.getLogger(__name__)


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        minutes_timeout = get_minutes_timeout()
        set_session_timeout_inactivity(request, minutes_timeout)


class UploadsListView(ListView):
    # model = InterfaceCall
    context_object_name = 'uploads_list'
    template_name = 'rm/uploads_list.html'

    # ordering = ['-date_time_creation'] is done through DataTables in JavaScript (see custom.css)

    def get_queryset(self):
        result = []
        user: CustomUser = self.request.user
        for call in InterfaceCall.objects.all():
            if user.has_perm_for_org_unit(*call.org_units):
                call.user_has_perm_for_org_units = True
            else:
                call.user_has_perm_for_org_units = False
            result.append(call)
        return result


@permission_required('rm.contracten_view', raise_exception=True)
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
    if dataset_type_name.lower() == CONTRACTEN.lower() and user.has_perm("rm.contracten_view"):
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
            details_url = get_dataset_details_url(
                dataset_type_name=dpou.interface_call.interface_definition.data_set_type.name,
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


def has_interface_call_the_right_datatype(interface_call,
                                          view_datatype) -> bool:
    """
    If the datatype is not known (then it has no data either) or when the datatype
    of the interface_call is the same as the view, it is allowed to show it.
    """
    if not interface_call.interface_definition:
        return True
    if interface_call.datatype == view_datatype:
        return True
    else:
        return False


class GenericUploadView(PermissionRequiredMixin, TemplateView):
    """
    A base class for uploading files and/or displaying the content of an upload.
    There are 2 levels of permissions for this view:
    1) the permission_required as defined below, for activating this view
    2) the permission required to upload/activate/deactivate

    """
    form_class = UploadFileForm

    permission_required = "rm.<<objecten>>_view"
    permission_required_for_upload = "rm.<<objecten>>_upload"
    template_name = 'rm/<<objecten>>_upload_details.html'

    # fields that define the upload behaviour
    url_name = "<<objecten>>_upload_details"
    page_title = "<<Objecten>> Upload Details"
    data_set_type_name = UNKNOWN
    expected_system = UNKNOWN
    breadcrumbs = {"home": "Home",
                   "uploads_list": "Uploads",
                   "active": "Contracten Upload Details"}

    def post(self, request, *args, **kwargs):

        # ACTIVATE
        if request.POST.get("activate"):
            call_id = request.POST.get("interface_call_id")
            call = InterfaceCall.objects.get(pk=int(call_id))
            call.activate_interface_call(start_transaction=True, cascading=True)
            logger.debug(f"Call: {call_id} activated")
            return HttpResponseRedirect(reverse(self.url_name, args=(call_id,)))

        # DEACTIVATE
        if request.POST.get("deactivate"):
            call_id = request.POST.get("interface_call_id")
            call = InterfaceCall.objects.get(pk=int(call_id))
            call.deactivate_interface_call(start_transaction=True)
            logger.debug(f"Call: {call_id} deactivated")
            return HttpResponseRedirect(reverse(self.url_name, args=(call_id,)))

        # UPLOAD
        form: UploadFileForm = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            logger.debug(f"Start upload file")
            file = request.FILES['file']
            call_id, status, msg = process_file(file=file,
                                                user=request.user,
                                                expected_system=self.expected_system)
            logger.debug(f"Call: {call_id} uploaded")
            return HttpResponseRedirect(reverse(self.url_name, args=(call_id,)))

        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user: CustomUser = request.user
        if pk:
            call: InterfaceCall = get_object_or_404(InterfaceCall, pk=pk)
            if not has_interface_call_the_right_datatype(interface_call=call,
                                                         view_datatype=self.data_set_type_name):
                raise PermissionDenied
            if not user.has_perm_for_org_unit(*call.org_units):
                raise PermissionDenied

        user_has_permission_for_upload = user.is_superuser or \
                                         user.has_perm(self.permission_required_for_upload)

        form = self.form_class()
        context = {'form': form,
                   'url_name': self.url_name,
                   'page_title': self.page_title,
                   'breadcrumbs': self.breadcrumbs,
                   'user_has_permission_for_upload': user_has_permission_for_upload}

        if pk:
            context = {**context,
                       **create_interface_call_context(pk, self.data_set_type_name)}
        return render(request, self.template_name, context)


def create_interface_call_context(pk, datasettype_name):
    """
    create the context for this interface_call, depending on datasettype_name
    """
    interface_call = InterfaceCall.objects.get(pk=pk)

    if datasettype_name == CONTRACTEN:
        stage_contracts_dict = interface_call.stage_contracts_per_org()
    else:
        raise SystemError(f"DataSetType_name: {datasettype_name} is not defined, programming error")

    raw_data = interface_call.rawdata_set.all().order_by("seq_nr")
    context = {
        'interface_call': interface_call,
        'stage_contract_dict': stage_contracts_dict,
        'received_data': raw_data,
    }
    return context


class ContractenUploadView(GenericUploadView):
    """
    View for uploading Contracten, started from the Interfaces list page
    """
    permission_required = "rm.contracten_upload"
    permission_required_for_upload = "rm.contracten_upload"

    template_name = 'rm/contracten_upload.html'

    # fields that define the upload behaviour
    url_name = "contracten_upload"
    page_title = "Contracten Upload"
    data_set_type_name = CONTRACTEN
    expected_system = NEGOMETRIX
    breadcrumbs = {"home": "Home",
                   "interface_list": "Interfaces",
                   "active": "Contracten Upload"}


class ContractenUploadDetailsView(GenericUploadView):
    """
    View for viewing, activating and deactivating Contracten uploads, started from the Uploads list page
    """
    permission_required = "rm.contracten_view"  # Yes, view, if user has _upload as well it sees the buttons
    permission_required_for_upload = "rm.contracten_upload"
    template_name = 'rm/contracten_upload.html'

    # fields that define the upload behaviour
    url_name = "contracten_upload_details"
    page_title = "Contracten Upload Details"
    data_set_type_name = CONTRACTEN
    expected_system = NEGOMETRIX
    breadcrumbs = {"home": "Home",
                   "uploads_list": "Uploads",
                   "active": "Contracten Upload Details"}


def create_contracten_dataset_context(dpou):
    stage_contracts_list = dpou.stagecontract_set.all().order_by("seq_nr")
    raw_data = dpou.interface_call.rawdata_set.all().order_by("seq_nr")
    context = {
        'dpou': dpou,
        'stage_contract_list': stage_contracts_list,
        'raw_data': raw_data,
    }
    return context


class ContractenDatasetDetailsView(PermissionRequiredMixin, DetailView):
    model = DataPerOrgUnit
    permission_required = "rm.contracten_view"
    context_object_name = 'dataset'
    template_name = 'rm/contracten_dataset_details.html'
    form_class = DatasetForm

    def post(self, request, *args, **kwargs):
        logger.debug("POST")

        # ACTIVATE
        if request.POST.get("activate"):
            dpou_id = request.POST.get("dpou_id")
            dpou = DataPerOrgUnit.objects.get(pk=int(dpou_id))
            errormessage = dpou.activate_dataset(start_transaction=True)
            if errormessage:
                messages.add_message(request, messages.ERROR, errormessage)
            logger.debug(f"DPOU: {dpou_id} activated")
            return HttpResponseRedirect(reverse('contracten_dataset_details', args=(dpou_id,)))

        # DEACTIVATE
        if request.POST.get("deactivate"):
            dpou_id = request.POST.get("dpou_id")
            dpou = DataPerOrgUnit.objects.get(pk=int(dpou_id))
            dpou.deactivate_dataset(start_transaction=True)
            logger.debug(f"DPOU: {dpou_id} deactivated")
            return HttpResponseRedirect(reverse('contracten_dataset_details', args=(dpou_id,)))

        return render(request, reverse("contracten_dataset_details"))

    def get(self, request, *args, **kwargs):
        dpou = self.get_object()
        errormessage = None
        if len(args) == 2:
            errormessage = args[1]

        if not dpou.get_data_set_type().name == CONTRACTEN:
            raise PermissionDenied
        form = self.form_class()
        context = {'form': form,
                   'errormessage': errormessage}
        context = {**context, **create_contracten_dataset_context(dpou)}
        return render(request, self.template_name, context)

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView

from stage.models import StageContract


class StageContractListView(PermissionRequiredMixin, ListView):
    permission_required = 'rm.contracten_view'
    raise_exception = True

    model = StageContract
    context_object_name = 'stage_contract_list'
    template_name = 'stage/stage_contract_list.html'

    def get_queryset(self):
        user = self.request.user
        return StageContract.objects.all()
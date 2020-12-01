from django.shortcuts import render
from django.views.generic import ListView

from rm.models import Contract


class ContractListView(ListView):
    model = Contract
    context_object_name = 'contract_list'
    template_name = 'rm/contract_list.html'

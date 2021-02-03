from django.urls import path

from . import views
from .views import StageContractListView

urlpatterns = [
    path('stage_contracts/', StageContractListView.as_view(), name='stage_contract_list'),
]

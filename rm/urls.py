from django.urls import path

from . import views
from .views import ContractListView, upload_file, InterfaceCallListView

urlpatterns = [
    path('', InterfaceCallListView.as_view(), name='interface_call_list'),
    path('interfacecall/<int:pk>/', views.interface_call_details),
    path('contract/', ContractListView.as_view(), name='contract_list'),
    path('upload/', upload_file, name="upload"),
]

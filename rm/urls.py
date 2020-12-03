from django.urls import path

from .views import ContractListView, upload_file

urlpatterns = [
    path('', ContractListView.as_view(), name='contract_list'),
    path('upload/', upload_file, name="upload"),
]

from django.urls import path, re_path

from . import views
from .views import UploadsListView, HomePageView, DataSetListView, InterfaceListView, \
    ContractenUploadView, ContractenUploadDetailsView, ContractenDatasetDetailsView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('interfaces', InterfaceListView.as_view(), name='interface_list'),
    path('uploads', UploadsListView.as_view(), name='uploads_list'),
    re_path(r'^datasets/$', DataSetListView.as_view(), name="dataset_list"),
    path('interfacecall/<int:pk>/', views.interface_call_details),
    path('contracten_upload/', ContractenUploadView.as_view(), name="contracten_upload"),
    path('contracten_upload/<int:pk>/', ContractenUploadView.as_view(), name="contracten_upload"),
    path('contracten_upload_details/', ContractenUploadDetailsView.as_view(), name="contracten_upload_details"),
    path('contracten_upload_details/<int:pk>/', ContractenUploadDetailsView.as_view(), name="contracten_upload_details"),
    path('contracten_dataset_details/', ContractenDatasetDetailsView.as_view(), name="contracten_dataset_details"),
    path('contracten_dataset_details/<int:pk>/', ContractenDatasetDetailsView.as_view(), name="contracten_dataset_details"),

]

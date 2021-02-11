from django.urls import path, re_path

from . import views
from .views import upload_file, InterfaceCallListView, HomePageView, DataSetListView, InterfaceListView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('interfaces', InterfaceListView.as_view(), name='interface_list'),
    path('interfacecalls', InterfaceCallListView.as_view(), name='interface_call_list'),
    re_path(r'^datasets/$', DataSetListView.as_view(), name="dataset_list"),
    path('interfacecall/<int:pk>/', views.interface_call_details),
    path('upload/', upload_file, name="contracten_upload"),
]

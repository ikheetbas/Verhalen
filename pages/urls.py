from django.urls import path

from . import views
from .views import Changelog

urlpatterns = [
    path('changelog', Changelog.as_view(), name='changelog'),
]

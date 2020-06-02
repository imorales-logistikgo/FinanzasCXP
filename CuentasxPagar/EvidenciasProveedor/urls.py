from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.EvidenciasProveedor, name='EvidenciasProveedor'),
    path('FindFolioProveedor', views.FindFolioProveedor, name='FindFolioProveedor'),
]

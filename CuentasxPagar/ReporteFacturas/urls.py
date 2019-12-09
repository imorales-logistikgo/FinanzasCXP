from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReporteFacturas, name='ReporteFacturas'),
    path('FilterBy', views.GetFacturasByFilters, name='GetFacturasByFilters'),
]

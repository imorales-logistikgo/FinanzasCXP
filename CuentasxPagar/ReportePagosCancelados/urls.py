from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportePagosCancelados, name='ReportePagosCancelados'),
    path('FilterBy', views.GetPagosByFilters, name='GetPagosByFilters'),
]

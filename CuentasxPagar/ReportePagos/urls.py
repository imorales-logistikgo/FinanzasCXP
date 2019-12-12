from django.urls import path
from . import views
urlpatterns = [
    path('', views.ReportePagos, name='ReportePagos'),
    path('FilterBy', views.GetPagosByFilters, name='GetPagosByFilters'),
]

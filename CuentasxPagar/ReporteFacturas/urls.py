from django.urls import path
from . import views
from django.shortcuts import redirect
from django.conf.urls import url

urlpatterns = [
    path('', views.ReporteFacturas, name='ReporteFacturas'),
    path('FilterBy', views.GetFacturasByFilters, name='GetFacturasByFilters'),
    url(r'^GetReporteTotales/(?P<Status>[\w-]+),(?P<Status2>[\w-]+)/$', views.GetReporteTotales),
    url(r'^GetReporteTotales/(?P<Status>[\w-]+)/$', views.GetReporteTotales,),
]

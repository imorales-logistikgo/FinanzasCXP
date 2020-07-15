from django.urls import path
from . import views
urlpatterns = [
    path('', views.ReportePagos, name='ReportePagos'),
    path('FilterBy', views.GetPagosByFilters, name='GetPagosByFilters'),
    path('CancelarPago', views.CancelarPago, name='CancelarPago'),
    path('GetDetallesPago', views.GetDetallesPago, name='GetDetallesPago'),
    path('SaveComplementosPago', views.SaveComplementosPago, name='SaveComplementosPago'),
    path('GetFacturasxPago', views.GetFacturasxPago, name='GetFacturasxPago'),
    path('GetFechaPago', views.GetFechaPago, name='GetFechaPago')
]

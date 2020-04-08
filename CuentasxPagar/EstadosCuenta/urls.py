from django.urls import path
from . import views
urlpatterns = [
    path('', views.EstadosdeCuenta, name='EstadosCuenta'),
    path('FilterBy', views.GetFacturasByFilters, name='FilterBy'),
    path('CancelarFactura', views.CancelarFactura, name='CancelarFactura'),
    path('GetDetallesFactura', views.GetDetallesFactura, name='GetDetallesFactura'),
    path('SavePagoxProveedor', views.SavePagoxProveedor, name='SavePagoxProveedor'),
    path('SavePagoxFactura', views.SavePagoxFactura, name='SavePagoxFactura'),
    path('CheckFolioDuplicado', views.CheckFolioDuplicado, name='CheckFolioDuplicado'),
    path('ValidarFactura', views.ValidarFactura, name='ValidarFactura'),
    path('EnviarCorreoProveedor', views.EnviarCorreoProveedor, name='EnviarCorreoProveedor'),
    path('GetDetallesPago', views.GetDetallesPago, name='GetDetallesPago'),
    path('GetDataReajuste', views.GetDataReajuste, name='GetDataReajuste'),
    path('GetAccesoriosxViaje', views.GetAccesoriosxViaje, name='GetAccesoriosxViaje'),
    path('GetRepartosxViaje', views.GetRepartosxViaje, name='GetRepartosxViaje'),
    path('saveReajuste', views.saveReajuste, name='saveReajuste')
    # path('FixIDProveedor', views.FixIDProveedor, name='FixIDProveedor')
]

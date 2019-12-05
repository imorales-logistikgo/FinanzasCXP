from django.urls import path
from . import views
urlpatterns = [
    path('', views.EstadosdeCuenta, name='EstadosCuenta'),
    path('FilterBy', views.GetFacturasByFilters, name='FilterBy'),
    path('CancelarFactura', views.CancelarFactura, name='CancelarFactura'),
    path('GetDetallesFactura', views.GetDetallesFactura, name='GetDetallesFactura'),
    path('SaveCobroxProveedor', views.SaveCobroxProveedor, name='SaveCobroxProveedor'),
    path('SaveCobroxFactura', views.SaveCobroxFactura, name='SaveCobroxFactura'),
]

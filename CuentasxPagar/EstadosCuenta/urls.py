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
]

from django.urls import path
from . import views

urlpatterns = [
    path("", views.Dashboard, name="Dashboard"),
    path('ManualPDF', views.ManualPDF, name='ManualPDF'),
    path('CrearUsuario', views.AltaUsuarioProveedor, name='CrearUsuario'),
    path('GetEvidencias', views.GetEvidenciasByFolio, name='GetEvidencias'),
    path('GeneradorPassword', views.GeneradorPassword, name='GeneradorPassword'),
    path('BloquearAccesoProveedor', views.BloquearAccesoProveedor, name='BloquearAccesoProveedor'),
    path('DesbloquearAccesoProveedor', views.DesbloquearAccesoProveedor, name='DesbloquearAccesoProveedor'),
    path('UpdatePassword', views.UpdatePassword, name='UpdatePassword'),
    path('GetDetallesCorreo', views.GetDetallesCorreo, name='GetDetallesCorreo'),
    path('AddCorreoByTransportista', views.AddCorreoByTransportista, name='AddCorreoByTransportista'),
    path('ActivarOrDesactivarCorreoToSendEmail', views.ActivarOrDesactivarCorreoToSendEmail, name='ActivarOrDesactivarCorreoToSendEmail')
]

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.EvidenciasProveedor, name='EvidenciasProveedor'),
    path('FindFolioProveedor', views.FindFolioProveedor, name='FindFolioProveedor'),
    path('SaveEvidencias', views.SaveEvidencias, name='SaveEvidencias'),
    path('GetEvidenciasMesaControl', views.GetEvidenciasMesaControl, name='GetEvidenciasMesaControl'),
    path('SaveAprobarEvidencia', views.SaveAprobarEvidencia, name='SaveAprobarEvidencia'),
    path('RechazarEvidencias', views.RechazarEvidencias, name='RechazarEvidencias'),
    path('GetEvidenciaFisica', views.GetEvidenciaFisica, name='GetEvidenciaFisica'),
    path('SaveEvidenciaFisica', views.SaveEvidenciaFisica, name='SaveEvidenciaFisica'),
    path('EvidenciaDigitalCompleta', views.EvidenciaDigitalCompleta, name='EvidenciaDigitalCompleta'),
    path('EvidenciaDigitalCompletaBKG', views.EvidenciaDigitalCompletaBKG, name='EvidenciaDigitalCompletaBKG'),
    path('ValidarEvidenciaXD_Viajea', views.ValidarEvidenciaXD_Viajea, name='ValidarEvidenciaXD_Viajea'),
    path('FindFolioEvidenciaBGK', views.FindFolioEvidenciaBGK, name='FindFolioEvidenciaBGK'),
    path('GetEachRemision', views.GetEachRemision, name='GetEachRemision'),
    path('DescargarHojaLiberacion', views.DescargarHojaLiberacion, name='DescargarHojaLiberacion'),
]

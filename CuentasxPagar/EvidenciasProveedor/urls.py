from django.conf.urls import url
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.EvidenciasProveedor, name='EvidenciasProveedor'),
    path('FindFolioProveedorE', views.FindFolioProveedorE, name='FindFolioProveedorE'),
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
    path('JsonEvidenciasBKG', views.JsonEvidenciasBKG, name='JsonEvidenciasBKG'),
    path('FilterBy', views.FilterBy, name='FilterBy'),
    path("uploadEvidencias", views.uploadEvidencias, name="uploadEvidencias"),
    path('descarga', views.descarga, name='descarga'),
    path('fechaevidencias', views.fechaevidencias, name='fechaevidencias'),
    path('fechaevdigital', views.fechaevdigital, name='fechaevdigital'),
    path('GetEvidenciasCXP', views.GetEvidenciasCXP, name='GetEvidenciasCXP'),
    path('GetObservacionesByPedidos', views.GetObservacionesByPedidos, name='GetObservacionesByPedidos'),
    path('GetEvidenciasMC', views.GetEvidenciasMC, name='GetEvidenciasMC'),
    url(r'^DownloadHojaLiberacion/(?P<IDViaje>[\w-]+)/(?P<Folio>[\w-]+)/$', views.DownloadHojaLiberacion),
    path('AllEvServiciosTrue', views.AllEvServiciosTrue, name='AllEvServiciosTrue')
]
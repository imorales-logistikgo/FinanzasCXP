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
]

from django.urls import path
from . import views

urlpatterns = [
    path("", views.GetPendientesEnviar, name='PendienteEnviar'),
	path("FilterBy", views.GetPendientesByFilters, name='FilterBy'),
	path("SaveFactura", views.SaveFacturaxProveedor, name='SaveFactura'),
	path("SavePartidasxFactura", views.SavePartidasxFactura, name='SavePartidasxFactura'),
]
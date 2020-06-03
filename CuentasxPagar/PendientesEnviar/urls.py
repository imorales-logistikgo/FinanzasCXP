from django.urls import path
from . import views

urlpatterns = [
    path("", views.GetPendientesEnviar, name='PendienteEnviar'),
	path("FilterBy", views.GetPendientesByFilters, name='FilterBy'),
	path("SaveFactura", views.SaveFacturaxProveedor, name='SaveFactura'),
	path("SavePartidasxFactura", views.SavePartidasxFactura, name='SavePartidasxFactura'),
	path("CheckFolioDuplicado", views.CheckFolioDuplicado, name='CheckFolioDuplicado'),
	path("FindFolioProveedor", views.FindFolioProveedor, name='FindFolioProveedor'),
	# path("CrearUsuariosTranportistas", views.CrearUsuariosTranportistas, name='CrearUsuariosTranportistas'),
    path("GetSerieProveedor", views.GetSerieProveedor, name='GetSerieProveedor'),
    path("GetProveedorByID", views.GetProveedorByID, name='GetProveedorByID'),
    #path("leerExcel", views.leerExcel, name='leerExcel'),


]

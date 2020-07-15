from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import FacturasxProveedor, RelacionFacturaProveedorxPartidas, RelacionConceptoxProyecto, View_ReporteFacturasCXP
from usersadmon.models import Proveedor
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
@login_required

def ReporteFacturas(request):
	if request.user.roles == 'Proveedor':
		Facturas = View_ReporteFacturasCXP.objects.filter(IDProveedor = request.user.IDTransportista).exclude(Status = 'DEPURADO')
		# listFacturas = FacturasToList(Facturas)
		ContadorPendientes, ContadorPagadas, ContadorAbonadas, ContadorCanceladas = GetContadores()
		Proveedores = Proveedor.objects.all()
		return render(request, 'ReporteFacturas.html', {'Facturas': Facturas, 'Proveedores': Proveedores, 'ContadorPagadas': ContadorPagadas, 'ContadorAbonadas': ContadorAbonadas, 'ContadorCanceladas': ContadorCanceladas, 'Rol': request.user.roles})
	else:
		Facturas = View_ReporteFacturasCXP.objects.exclude(Status__in= ('CANCELADA','DEPURADO'))
		# listFacturas = FacturasToList(Facturas)
		ContadorPendientes, ContadorPagadas, ContadorAbonadas, ContadorCanceladas = GetContadores()
		Proveedores = Proveedor.objects.all()
		return render(request, 'ReporteFacturas.html', {'Facturas': Facturas, 'Proveedores': Proveedores, 'ContadorPagadas': ContadorPagadas, 'ContadorAbonadas': ContadorAbonadas, 'ContadorCanceladas': ContadorCanceladas, 'ContadorPendientes': ContadorPendientes, 'Rol': request.user.roles})



def FacturasToList(Facturas):
	listFacturas = list()
	for Fact in Facturas:
		Factura = {}
		conFacturaxPartidas = RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = Fact.IDFactura).select_related('IDPendienteEnviar')
		Factura['Folio'] = Fact.Folio
		Factura['Proveedor'] = Fact.NombreCortoProveedor
		Factura['FechaFactura'] = Fact.FechaFactura
		Factura["Subtotal"] = Fact.Subtotal
		Factura["IVA"] = Fact.IVA
		Factura["Retencion"] = Fact.Retencion
		Factura["Status"] = Fact.Status
		Factura['Total'] = Fact.Total
		Factura['Viajes'] = ''
		for PENDIENTE in conFacturaxPartidas:
			Factura['Viajes'] += PENDIENTE.IDPendienteEnviar.Folio + ", "
		Factura['Viajes'] = Factura['Viajes'][:-2]
		Factura["ComentarioBaja"] = Fact.ComentarioBaja
		listFacturas.append(Factura)
	return listFacturas



def GetContadores():
	AllFacturas = list(View_ReporteFacturasCXP.objects.values("Status").all())
	ContadorPendientes = len(list(filter(lambda x: x["Status"] == "PENDIENTE", AllFacturas)))
	ContadorPagadas = len(list(filter(lambda x: x["Status"] == "PAGADA", AllFacturas)))
	ContadorAbonadas = len(list(filter(lambda x: x["Status"] == "ABONADA", AllFacturas)))
	ContadorCanceladas = len(list(filter(lambda x: x["Status"] == "CANCELADA", AllFacturas)))
	return ContadorPendientes, ContadorPagadas, ContadorAbonadas, ContadorCanceladas


def GetFacturasByFilters(request):
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	Status = json.loads(request.GET["Status"])
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		Facturas = View_ReporteFacturasCXP.objects.filter(FechaFactura__month__in = arrMonth, FechaFactura__year = Year).exclude(Status = 'DEPURADO')
	else:
		Facturas = View_ReporteFacturasCXP.objects.filter(FechaFactura__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')]).exclude(Status = 'DEPURADO')
	if Proveedores:
		Facturas = Facturas.filter(NombreCortoProveedor__in = Proveedores)
	if Moneda:
		Facturas = Facturas.filter(Moneda__in = Moneda)
	if Status:
		Facturas = Facturas.filter(Status__in = Status).exclude(Status = 'DEPURADO')
	# listFacturas = FacturasToList(Facturas)
	htmlRes = render_to_string('TablaReporteFacturas.html', {'Facturas':Facturas}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})

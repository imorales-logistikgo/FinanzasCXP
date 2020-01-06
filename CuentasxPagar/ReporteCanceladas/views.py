from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import FacturasxProveedor, RelacionFacturaProveedorxPartidas, RelacionConceptoxProyecto
from usersadmon.models import Proveedor
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
@login_required

def ReporteCanceladas(request):
	Canceladas = FacturasxProveedor.objects.filter(Status = 'Cancelada')
	listFacturas = CanceladasToList(Canceladas)
	Proveedores = Proveedor.objects.all()
	return render(request, 'ReporteCanceladas.html', {'Facturas': listFacturas, 'Proveedores': Proveedores, 'Rol': request.user.roles})



def CanceladasToList(Canceladas):
	listFacturas = list()
	for Cancelada in Canceladas:
		Factura = {}
		conFacturaxPartidas = RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = Cancelada.IDFactura).select_related('IDPendienteEnviar').select_related('IDPartida')
		Factura['Folio'] = Cancelada.Folio
		Factura['Proveedor'] = Cancelada.NombreCortoProveedor
		Factura['FechaFactura'] = Cancelada.FechaFactura
		Factura['FechaBaja'] = list(conFacturaxPartidas)[0].IDPartida.FechaBaja
		Factura["Subtotal"] = Cancelada.Subtotal
		Factura["IVA"] = Cancelada.IVA
		Factura["Retencion"] = Cancelada.Retencion
		Factura['Total'] = Cancelada.Total
		Factura['Viajes'] = ''
		for Pendiente in conFacturaxPartidas:
			Factura['Viajes'] += Pendiente.IDPendienteEnviar.Folio + ", "
		Factura['Viajes'] = Factura['Viajes'][:-2]
		listFacturas.append(Factura)
	return listFacturas



def GetCanceladasByFilters(request):
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		Canceladas = FacturasxProveedor.objects.filter(FechaFactura__month__in = arrMonth, FechaFactura__year = Year, Status = "Cancelada")
	else:
		Canceladas = FacturasxProveedor.objects.filter(FechaFactura__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')], Status = "Cancelada")
	if Proveedores:
		Canceladas = Canceladas.filter(NombreCortoProveedor__in = Proveedores)
	if Moneda:
		Canceladas = Canceladas.filter(Moneda__in = Moneda)
	listFacturas = CanceladasToList(Canceladas)
	htmlRes = render_to_string('TablaReporteCanceladas.html', {'Facturas':listFacturas}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})

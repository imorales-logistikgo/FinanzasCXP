from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import FacturasxProveedor, RelacionFacturaProveedorxPartidas, RelacionConceptoxProyecto
from usersadmon.models import Proveedor
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
@login_required

def ReporteCanceladas(request):
	Canceladas = FacturasxProveedor.objects.filter(Status = 'CANCELADA')
	listFacturas = CanceladasToList(Canceladas)
	Proveedores = Proveedor.objects.all()
	return render(request, 'ReporteCanceladas.html', {'Facturas': listFacturas, 'Proveedores': Proveedores, 'Rol': request.user.roles})



def CanceladasToList(Canceladas):
	listFacturas = list()
	for CANCELADA in Canceladas:
		Factura = {}
		conFacturaxPartidas = RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = CANCELADA.IDFactura).select_related('IDPendienteEnviar').select_related('IDPartida')
		Factura['Folio'] = CANCELADA.Folio
		Factura['Proveedor'] = CANCELADA.NombreCortoProveedor
		Factura['FechaFactura'] = CANCELADA.FechaFactura
		try:
			Factura['FechaBaja'] = list(conFacturaxPartidas)[0].IDPartida.FechaBaja
		except:
			Factura['FechaBaja'] = ""
		Factura["Subtotal"] = CANCELADA.Subtotal
		Factura["IVA"] = CANCELADA.IVA
		Factura["Retencion"] = CANCELADA.Retencion
		Factura['Total'] = CANCELADA.Total
		Factura['Viajes'] = ''
		for PENDIENTE in conFacturaxPartidas:
			Factura['Viajes'] += PENDIENTE.IDPendienteEnviar.Folio + ", "
		Factura['Viajes'] = Factura['Viajes'][:-2]
		listFacturas.append(Factura)
	return listFacturas



def GetCanceladasByFilters(request):
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		Canceladas = FacturasxProveedor.objects.filter(FechaFactura__month__in = arrMonth, FechaFactura__year = Year, Status = "CANCELADA")
	else:
		Canceladas = FacturasxProveedor.objects.filter(FechaFactura__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')], Status = "CANCELADA")
	if Proveedores:
		Canceladas = Canceladas.filter(NombreCortoProveedor__in = Proveedores)
	if Moneda:
		Canceladas = Canceladas.filter(Moneda__in = Moneda)
	listFacturas = CanceladasToList(Canceladas)
	htmlRes = render_to_string('TablaReporteCanceladas.html', {'Facturas':listFacturas}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})

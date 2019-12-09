from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import FacturasxProveedor, RelacionFacturaProveedorxPartidas, RelacionConceptoxProyecto
from django.template.loader import render_to_string
import json, datetime


def ReporteCanceladas(request):
	Canceladas = FacturasxProveedor.objects.filter(Status = 'Cancelada')
	listFacturas = list()
	for Cancelada in Canceladas:
		Factura = {}
		conFacturaxPartidas= RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = Cancelada.IDFactura)
		Factura['Folio'] = Cancelada.Folio
		Factura['Proveedor'] = Cancelada.NombreCortoProveedor
		Factura['FechaFactura'] = Cancelada.FechaFactura
		Factura['FechaBaja'] = conFacturaxPartidas.first().IDPartida.FechaBaja
		Factura['Total'] = Cancelada.Total
		Factura['Viajes'] = ''
		for Pendiente in conFacturaxPartidas:
			Factura['Viajes'] += RelacionConceptoxProyecto.objects.get(IDConcepto = Pendiente.IDConcepto).IDPendienteEnviar.Folio + ", "
		Factura['Viajes'] = Factura['Viajes'][:-2]
		listFacturas.append(Factura)
	return render(request, 'ReporteCanceladas.html', {'Facturas': listFacturas})



def GetCanceladasByFilters(request):
	FechaFacturaDesde = request.GET["FechaFacturaDesde"]
	FechaFacturaHasta = request.GET["FechaFacturaHasta"]
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	if not Proveedores:
		Canceladas = FacturasxProveedor.objects.filter(Status = 'Cancelada')
	else:
		Canceladas = FacturasxProveedor.objects.filter(Status = 'Cancelada', NombreCortoProveedor__in = Proveedores)
	if Moneda:
		Canceladas = Canceladas.filter(Moneda__in = Moneda)
	Canceladas = Canceladas.filter(FechaFactura__range = [datetime.datetime.strptime(FechaFacturaDesde,'%m/%d/%Y'), datetime.datetime.strptime(FechaFacturaHasta,'%m/%d/%Y')])
	listFacturas = list()
	for Cancelada in Canceladas:
		Factura = {}
		conFacturaxPartidas= RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = Cancelada.IDFactura)
		Factura['Folio'] = Cancelada.Folio
		Factura['Cliente'] = Cancelada.NombreCortoProveedor
		Factura['FechaFactura'] = Cancelada.FechaFactura
		Factura['FechaBaja'] = conFacturaxPartidas.first().IDPartida.FechaBaja
		Factura['Total'] = Cancelada.Total
		Factura['Viajes'] = ''
		for Pendiente in conFacturaxPartidas:
			Factura['Viajes'] += RelacionConceptoxProyecto.objects.get(IDConcepto = Pendiente.IDConcepto).IDPendienteEnviar.Folio + ", "
		Factura['Viajes'] = Factura['Viajes'][:-2]
		listFacturas.append(Factura)
	htmlRes = render_to_string('TablaReporteCanceladas.html', {'Facturas':listFacturas}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})
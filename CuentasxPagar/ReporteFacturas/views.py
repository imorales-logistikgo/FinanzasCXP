from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import FacturasxProveedor, RelacionFacturaProveedorxPartidas, RelacionConceptoxProyecto
from django.template.loader import render_to_string
import json, datetime


def ReporteFacturas(request):
	Facturas = FacturasxProveedor.objects.all()
	listFacturas = list()
	for Fact in Facturas:
		Factura = {}
		conFacturaxPartidas= RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = Fact.IDFactura)
		Factura['Folio'] = Fact.Folio
		Factura['Proveedor'] = Fact.NombreCortoProveedor
		Factura['FechaFactura'] = Fact.FechaFactura
		Factura['FechaBaja'] = conFacturaxPartidas.first().IDPartida.FechaBaja
		Factura["Subtotal"] = Fact.Subtotal
		Factura["IVA"] = Fact.IVA
		Factura["Retencion"] = Fact.Retencion
		Factura['Total'] = Fact.Total
		Factura['Viajes'] = ''
		for Pendiente in conFacturaxPartidas:
			Factura['Viajes'] += RelacionConceptoxProyecto.objects.get(IDConcepto = Pendiente.IDConcepto).IDPendienteEnviar.Folio + ", "
		Factura['Viajes'] = Factura['Viajes'][:-2]
		listFacturas.append(Factura)
	return render(request, 'ReporteFacturas.html', {'Facturas': listFacturas})



def GetFacturasByFilters(request):
	FechaFacturaDesde = request.GET["FechaFacturaDesde"]
	FechaFacturaHasta = request.GET["FechaFacturaHasta"]
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	if not Proveedores:
		Facturas = FacturasxProveedor.objects.all()
	else:
		Facturas = FacturasxProveedor.objects.filter(NombreCortoProveedor__in = Proveedores)
	if Moneda:
		Facturas = Facturas.filter(Moneda__in = Moneda)
	Facturas = Facturas.filter(FechaFactura__range = [datetime.datetime.strptime(FechaFacturaDesde,'%m/%d/%Y'), datetime.datetime.strptime(FechaFacturaHasta,'%m/%d/%Y')])
	listFacturas = list()
	for Fact in Facturas:
		Factura = {}
		conFacturaxPartidas= RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = Fact.IDFactura)
		Factura['Folio'] = Fact.Folio
		Factura['Cliente'] = Fact.NombreCortoProveedor
		Factura['FechaFactura'] = Fact.FechaFactura
		Factura['FechaBaja'] = conFacturaxPartidas.first().IDPartida.FechaBaja
		Factura['Total'] = Fact.Total
		Factura['Viajes'] = ''
		for Pendiente in conFacturaxPartidas:
			Factura['Viajes'] += RelacionConceptoxProyecto.objects.get(IDConcepto = Pendiente.IDConcepto).IDPendienteEnviar.Folio + ", "
		Factura['Viajes'] = Factura['Viajes'][:-2]
		listFacturas.append(Factura)
	htmlRes = render_to_string('TablaReporteFacturas.html', {'Facturas':listFacturas}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})
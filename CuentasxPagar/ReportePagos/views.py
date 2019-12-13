from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from EstadosCuenta.models import RelacionPagosFacturasxProveedor, PagosxProveedor
from django.template.loader import render_to_string
import json, datetime


def ReportePagos(request):
	Pagos = PagosxProveedor.objects.exclude(Status = "Cancelada")
	Folios = list()
	for Pago in Pagos:
		FoliosFactura = ""
		for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = Pago.IDPago):
			FoliosFactura += Factura.IDFactura.Folio + ", "
		FoliosFactura = FoliosFactura[:-2]
		Folios.append(FoliosFactura)
	return render(request, 'ReportePagos.html', {"Pagos": Pagos, "Folios" : Folios});



def GetPagosByFilters(request):
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		Pagos = PagosxProveedor.objects.filter(FechaPago__month__in = arrMonth, FechaPago__year = Year).exclude(Status = "Cancelada")
	else:
		Pagos = PagosxProveedor.objects.filter(FechaPago__range = [datetime.datetime.strptime(request.GET["FechaPagoDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaPagoHasta"],'%m/%d/%Y')]).exclude(Status = "Cancelada")
	if Proveedores:
		Pagos = Pagos.filter(NombreCortoProveedor__in = Proveedores)
	Folios = list()
	for Pago in Pagos:
		FoliosFactura = ""
		for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = Pago.IDPago):
			FoliosFactura += Factura.IDFactura.Folio + ", "
		FoliosFactura = FoliosFactura[:-2]
		Folios.append(FoliosFactura)
	htmlRes = render_to_string('TablaReportePagos.html', {'Pagos':Pagos, 'Folios' : Folios}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def CancelarPago(request):
	IDPago = json.loads(request.body.decode('utf-8'))["IDPago"]
	for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = IDPago):
		Factura.IDFactura.Saldo += Factura.IDPagoxFactura.Total
		if Factura.IDFactura.Saldo == Factura.IDFactura.Total:
			Factura.IDFactura.Status = "Pendiente"
		else:
			Factura.IDFactura.Status = "Abonada"
		Factura.IDFactura.save()
	Pago = PagosxProveedor.objects.get(IDPago = IDPago)
	Pago.Status = "Cancelada"
	Pago.save()
	return HttpResponse('')

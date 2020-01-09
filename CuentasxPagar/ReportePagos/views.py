from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from EstadosCuenta.models import RelacionPagosFacturasxProveedor, PagosxProveedor, View_FacturasxProveedor, PagosxFacturas
from usersadmon.models import Proveedor
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
@login_required

def ReportePagos(request):
	Pagos = PagosxProveedor.objects.exclude(Status = "CANCELADA")
	Folios = list()
	for Pago in Pagos:
		FoliosFactura = ""
		for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = Pago.IDPago).select_related('IDFactura'):
			FoliosFactura += Factura.IDFactura.Folio + ", "
		FoliosFactura = FoliosFactura[:-2]
		Folios.append(FoliosFactura)
	Proveedores = Proveedor.objects.all()
	return render(request, 'ReportePagos.html', {"Pagos": Pagos, "Folios" : Folios, 'Proveedores': Proveedores, 'Rol': request.user.roles});



def GetPagosByFilters(request):
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		Pagos = PagosxProveedor.objects.filter(FechaPago__month__in = arrMonth, FechaPago__year = Year).exclude(Status = "CANCELADA")
	else:
		Pagos = PagosxProveedor.objects.filter(FechaPago__range = [datetime.datetime.strptime(request.GET["FechaPagoDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaPagoHasta"],'%m/%d/%Y')]).exclude(Status = "CANCELADA")
	if Proveedores:
		Pagos = Pagos.filter(NombreCortoProveedor__in = Proveedores)
	Folios = list()
	for Pago in Pagos:
		FoliosFactura = ""
		for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = Pago.IDPago).select_related('IDFactura'):
			FoliosFactura += Factura.IDFactura.Folio + ", "
		FoliosFactura = FoliosFactura[:-2]
		Folios.append(FoliosFactura)
	htmlRes = render_to_string('TablaReportePagos.html', {'Pagos':Pagos, 'Folios' : Folios}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def CancelarPago(request):
	IDPago = json.loads(request.body.decode('utf-8'))["IDPago"]
	for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = IDPago).select_related('IDFactura'):
		Factura.IDFactura.Saldo += Factura.IDPagoxFactura.Total
		if Factura.IDFactura.Saldo == Factura.IDFactura.Total:
			View_FacturasxProveedor.objects.get(IDFactura = Factura.IDFactura.IDFactura).Status = "PENDIENTE"
		else:
			View_FacturasxProveedor.objects.get(IDFactura = Factura.IDFactura.IDFactura).Status = "ABONADA"
		Factura.IDFactura.save()
	Pago = PagosxProveedor.objects.get(IDPago = IDPago)
	Pago.Status = "CanceladaS"
	Pago.IDUsuarioBaja = request.user
	Pago.FechaBaja = datetime.datetime.now()
	Pago.save()
	return HttpResponse('')



def GetDetallesPago(request):
	IDPago = request.GET["IDPago"]
	FacturasxPago = RelacionPagosFacturasxProveedor.objects.filter(IDPago = IDPago).select_related('IDFactura').select_related('IDPagoxFactura')
	Facturas = list()
	for FacturasxPago in FacturasxPago:
		Pago = {}
		#Factura = View_FacturasxProveedor.objects.get(IDFactura = FacturasxPago.IDFactura.IDFactura)
		Pago["FolioFactura"] = FacturasxPago.IDFactura.Folio
		Pago["FechaFactura"] = FacturasxPago.IDFactura.FechaFactura
		Pago["Total"] = FacturasxPago.IDPagoxFactura.Total
		Facturas.append(Pago)
	htmlRes = render_to_string('TablaDetallesPago.html', {'Facturas':Facturas}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})

def SaveComplementosPago(request):
	jParams = json.loads(request.body.decode('utf-8'))#["IDPago"]
	print(jParams)
	Pago = PagosxProveedor.objects.get(IDPago = jParams['IDPago'])
	Pago.RutaPDF = jParams['RutaPDF']
	Pago.RutaXML = jParams['RutaXML']
	Pago.save()
	return HttpResponse("")

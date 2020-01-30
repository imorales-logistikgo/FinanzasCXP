from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from EstadosCuenta.models import RelacionPagosFacturasxProveedor, PagosxProveedor, View_FacturasxProveedor
from usersadmon.models import Proveedor
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
@login_required

def ReportePagosCancelados(request):
	if request.user.roles == 'Proveedor':
		return render(request, '404.html')
	else:
		Pagos = PagosxProveedor.objects.defer("IDUsuarioAlta").filter(Status = "CANCELADA").select_related('IDUsuarioBaja')
		Folios = list()
		for Pago in Pagos:
			FoliosFactura = ""
			for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = Pago.IDPago).select_related('IDFactura'):
				FoliosFactura += Factura.IDFactura.Folio + ", "
			FoliosFactura = FoliosFactura[:-2]
			Folios.append(FoliosFactura)
		Proveedores = Proveedor.objects.all()
		return render(request, 'PagosCancelados.html', {"Pagos": Pagos, "Folios" : Folios, 'Proveedores': Proveedores, 'Rol': request.user.roles});




def GetPagosByFilters(request):
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		Pagos = PagosxProveedor.objects.filter(FechaPago__month__in = arrMonth, FechaPago__year = Year, Status = "CANCELADA")
	else:
		Pagos = PagosxProveedor.objects.filter(FechaPago__range = [datetime.datetime.strptime(request.GET["FechaPagoDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaPagoHasta"],'%m/%d/%Y')], Status = "CANCELADA")
	if Proveedores:
		Pagos = Pagos.filter(NombreCortoProveedor__in = Proveedores)
	Folios = list()
	for Pago in Pagos:
		FoliosFactura = ""
		for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = Pago.IDPago).select_related('IDFactura'):
			FoliosFactura += Factura.IDFactura.Folio + ", "
		FoliosFactura = FoliosFactura[:-2]
		Folios.append(FoliosFactura)
	htmlRes = render_to_string('TablaReportePagosCancelados.html', {'Pagos':Pagos, 'Folios' : Folios}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})

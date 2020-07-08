from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from EstadosCuenta.models import RelacionPagosFacturasxProveedor, PagosxProveedor, View_FacturasxProveedor, PagosxFacturas
from usersadmon.models import Proveedor, AdmonUsuarios
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect
@login_required

def ReportePagos(request):
	if request.user.roles == 'Proveedor':
		return redirect('Actualizacion')
		# Pagos = PagosxProveedor.objects.exclude(Status = "CANCELADA").filter(IDProveedor = request.user.IDTransportista)
		# Folios = list()
		# for Pago in Pagos:
		# 	FoliosFactura = ""
		# 	for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = Pago.IDPago).select_related('IDFactura'):
		# 		FoliosFactura += Factura.IDFactura.Folio + ", "
		# 	FoliosFactura = FoliosFactura[:-2]
		# 	Folios.append(FoliosFactura)
		# Proveedores = Proveedor.objects.all()
		# return render(request, 'ReportePagos.html', {"Pagos": Pagos, "Folios" : Folios, 'Proveedores': Proveedores, 'Rol': request.user.roles});
	else:
		Pagos = PagosxProveedor.objects.exclude(Status = "CANCELADA").filter(FechaPago__month = datetime.datetime.now().month, FechaPago__year = datetime.datetime.now().year)
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
	Motivo = json.loads(request.body.decode('utf-8'))["motivoEliminacion"]
	try:
		with transaction.atomic(using = 'users'):
			for Factura in RelacionPagosFacturasxProveedor.objects.filter(IDPago = IDPago).select_related('IDFactura'):
				Factura.IDFactura.Saldo += (Factura.IDPagoxFactura.Total/Factura.IDPago.TipoCambio) if (Factura.IDFactura.Moneda == 'USD') else Factura.IDPagoxFactura.Total
				if Factura.IDFactura.Saldo == Factura.IDFactura.Total:
					Factura.IDFactura.Status = "PENDIENTE"
				else:
					Factura.IDFactura.Status = "ABONADA"
				Factura.IDFactura.save()
			Pago = PagosxProveedor.objects.get(IDPago = IDPago)
			Pago.Status = "CANCELADA"
			Pago.IDUsuarioBaja = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
			Pago.FechaBaja = datetime.datetime.now()
			Pago.ComentarioBaja = Motivo
			Pago.save()
			return HttpResponse(status = 200)
	except Exception as e:
		transaction.rollback(using='users')
		print(e)
		return HttpResponse(status=400)



def GetDetallesPago(request):
	IDPago = request.GET["IDPago"]
	FacturasxPago = RelacionPagosFacturasxProveedor.objects.filter(IDPago = IDPago).select_related('IDFactura').select_related('IDPagoxFactura')
	Facturas = list()
	for FacturaxPago in FacturasxPago:
		Pago = {}
		#Factura = View_FacturasxProveedor.objects.get(IDFactura = FacturasxPago.IDFactura.IDFactura)
		Pago["FolioFactura"] = FacturaxPago.IDFactura.Folio
		Pago["FechaFactura"] = FacturaxPago.IDFactura.FechaFactura
		Pago["Total"] = FacturaxPago.IDPagoxFactura.Total
		Facturas.append(Pago)
	htmlRes = render_to_string('TablaDetallesReportePago.html', {'Facturas':Facturas}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})

def SaveComplementosPago(request):
	jParams = json.loads(request.body.decode('utf-8'))#["IDPago"]
	print(jParams)
	Pago = PagosxProveedor.objects.get(IDPago = jParams['IDPago'])
	Pago.RutaPDF = jParams['RutaPDF']
	Pago.RutaXML = jParams['RutaXML']
	Pago.save()
	return HttpResponse("")

def GetFacturasxPago(request):
	IDPago = request.GET["IDPago"]
	GetIDRelacion = RelacionPagosFacturasxProveedor.objects.filter(IDPago = IDPago)
	DataBD = list()
	for Factura in GetIDRelacion:
		Data = {}
		Data['IdDocumento'] = Factura.IDFactura.UUID
		Data['ImpPagado'] = Factura.IDPagoxFactura.Total
		DataBD.append(Data)
	return JsonResponse({"DataBD":DataBD})

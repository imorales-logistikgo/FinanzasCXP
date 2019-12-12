from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import RelacionFacturaProveedorxPartidas, FacturasxProveedor, PendientesEnviar, RelacionConceptoxProyecto
from EstadosCuenta.models import  View_FacturasxProveedor, PagosxProveedor, PagosxFacturas, RelacionPagosFacturasxProveedor
from django.template.loader import render_to_string
from decimal import Decimal
import json, datetime


def EstadosdeCuenta(request):
	FacturasPendiente = View_FacturasxProveedor.objects.filter(Status = "Pendiente")
	FacturasAbonada = View_FacturasxProveedor.objects.filter(Status = "Abonada")
	result = FacturasPendiente | FacturasAbonada
	Folios = list()
	for Factura in result:
		FoliosPago= ""
		for Pago in RelacionPagosFacturasxProveedor.objects.filter(IDFactura = Factura.IDFactura):
			FoliosPago += Pago.IDPago.Folio + ", "
		FoliosPago = FoliosPago[:-2]
		Folios.append(FoliosPago)
	ContadoresPendientes = len(list(FacturasPendiente))
	ContadoresAbonadas = len(list(FacturasAbonada))
	return render(request, 'EstadosdeCuenta.html', {'Facturas': result, 'Folios': Folios, 'ContadoresPendientes': ContadoresPendientes, 'ContadoresAbonadas': ContadoresAbonadas})



def GetFacturasByFilters(request):
	Proveedores = json.loads(request.GET["Proveedor"])
	Status = json.loads(request.GET["Status"])
	Moneda = json.loads(request.GET["Moneda"])
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		Facturas = View_FacturasxProveedor.objects.filter(FechaFactura__month__in = arrMonth, FechaFactura__year = Year)
	else:
		Facturas = View_FacturasxProveedor.objects.filter(FechaFactura__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')])
	if Status:
		Facturas = Facturas.filter(Status__in = Status)
	if Proveedores:
		Facturas = Facturas.filter(Proveedor__in = Proveedores)
	if Moneda:
		Facturas = Facturas.filter(Moneda__in = Moneda)
	Folios = list()
	for Factura in Facturas:
		FoliosPago= ""
		for Pago in RelacionPagosFacturasxProveedor.objects.filter(IDFactura = Factura.IDFactura):
			FoliosPago += Pago.IDPago.Folio + ", "
		FoliosPago = FoliosPago[:-2]
		Folios.append(FoliosPago)
	htmlRes = render_to_string('TablaEstadosCuenta.html', {'Facturas': Facturas, 'Folios': Folios}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def CancelarFactura(request):
	IDFactura = json.loads(request.body.decode('utf-8'))["IDFactura"]
	conRelacionFacturaProveedorxPartidas = RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = IDFactura)
	if conRelacionFacturaProveedorxPartidas:
		conRelacionFacturaProveedorxPartidas[0].IDFacturaxProveedor.Status = 'Cancelada'
		conRelacionFacturaProveedorxPartidas[0].IDFacturaxProveedor.save()
		for Partida in conRelacionFacturaProveedorxPartidas:
			Partida.IDPartida.IsActiva = False
			Partida.IDPartida.FechaBaja = datetime.datetime.now()
			conPendienteEnviar = RelacionConceptoxProyecto.objects.get(IDConcepto = Partida.IDConcepto)
			conPendienteEnviar.IDPendienteEnviar.IsFacturaProveedor = False
			conPendienteEnviar.IDPendienteEnviar.save()
			Partida.IDPartida.save()
	return HttpResponse("")



def GetDetallesFactura(request):
	ListaViajes = list()
	IDFactura = request.GET["IDFactura"]
	conRelacionFacturaProveedorxPartidas = RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = IDFactura)
	if conRelacionFacturaProveedorxPartidas:
		for Partida in conRelacionFacturaProveedorxPartidas:
			ListaViajes.append(RelacionConceptoxProyecto.objects.get(IDConcepto = Partida.IDConcepto))
	htmlRes = render_to_string('TablaDetallesFactura.html', {'Pendientes':ListaViajes}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def SavePagoxProveedor(request):
	jParams = json.loads(request.body.decode('utf-8'))
	newPago = PagosxProveedor()
	newPago.FechaAlta = datetime.datetime.now()
	newPago.Folio = jParams["Folio"]
	newPago.Total = jParams["Total"]
	newPago.FechaPago = datetime.datetime.strptime(jParams["FechaPago"],'%Y/%m/%d')
	if "RutaXML" in jParams:
		newPago.RutaXML = jParams["RutaXML"]
	if "RutaPDF" in jParams:
		newPago.RutaPDF = jParams["RutaPDF"]
	newPago.Comentarios = jParams["Comentarios"]
	newPago.TipoCambio = jParams["TipoCambio"]
	newPago.NombreCortoProveedor = jParams["Proveedor"]
	newPago.save()
	return HttpResponse(newPago.IDPago)



def SavePagoxFactura(request):
	jParams = json.loads(request.body.decode('utf-8'))
	for Pago in jParams["arrPagos"]:
		newPagoxFactura = PagosxFacturas()
		newPagoxFactura.Total = Pago["Total"]
		newPagoxFactura.FechaAlta = datetime.datetime.now()
		newPagoxFactura.save()
		newRelacionPagoxFactura = RelacionPagosFacturasxProveedor()
		newRelacionPagoxFactura.IDPago = PagosxProveedor.objects.get(IDPago = jParams["IDPago"])
		newRelacionPagoxFactura.IDPagoxFactura = PagosxFacturas.objects.get(IDPagoxFactura = newPagoxFactura.IDPagoxFactura)
		Factura = FacturasxProveedor.objects.get(IDFactura = Pago["IDFactura"])
		Factura.Saldo -= Decimal(Pago["Total"])
		newRelacionPagoxFactura.IDFactura = Factura
		newRelacionPagoxFactura.IDUsuarioAlta = 1
		newRelacionPagoxFactura.IDProveedor = 1
		if Factura.Saldo == 0:
			Factura.Status = "Cobrada"
		else:
			Factura.Status = "Abonada"
		Factura.save()
		newRelacionPagoxFactura.save()
	return HttpResponse("")



def CheckFolioDuplicado(request):
	IsDuplicated = PagosxProveedor.objects.filter(Folio = request.GET["Folio"]).exists()
	return JsonResponse({'IsDuplicated' : IsDuplicated})
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
	FechaDescargaDesde = request.GET["FechaDescargaDesde"]
	FechaDescargaHasta = request.GET["FechaDescargaHasta"]
	Proveedores = json.loads(request.GET["Proveedor"])
	Status = json.loads(request.GET["Status"])
	Moneda = json.loads(request.GET["Moneda"])
	Facturas = View_FacturasxProveedor.objects.filter(FechaFactura__range = [datetime.datetime.strptime(FechaDescargaDesde,'%m/%d/%Y'), datetime.datetime.strptime(FechaDescargaHasta,'%m/%d/%Y')])
	if Status:
		Facturas = Facturas.filter(Status__in = Status)
	if Proveedores:
		Facturas = Facturas.filter(NombreCortoProveedor__in = Proveedores)
	if Moneda:
		Facturas = Facturas.filter(Moneda__in = Moneda)
	Folios = list()
	for Factura in Facturas:
		FoliosPago= ""
		for Pago in RelacionPagosFacturasxProveedor.objects.filter(IDFactura = Factura.IDFactura):
			FoliosPago += Pago.IDPago.Folio + ", "
		FoliosPago = FoliosPago[:-2]
		Folios.append(FoliosPago)
	htmlRes = render_to_string('TablaEstadosCuenta.html', {'Facturas':Facturas, 'Folios': Folios}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def CancelarFactura(request):
	IDFactura = json.loads(request.body.decode('utf-8'))["IDFactura"]
	conRelacionFacturaxPartidas = RelacionFacturaxPartidas.objects.filter(IDFacturaxProveedor = IDFactura)
	if conRelacionFacturaxPartidas:
		conRelacionFacturaxPartidas[0].IDFacturaxProveedor.Status = 'Cancelada'
		conRelacionFacturaxPartidas[0].IDFacturaxProveedor.save()
		for Partida in conRelacionFacturaxPartidas:
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
	conRelacionFacturaxPartidas = RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = IDFactura)
	if conRelacionFacturaxPartidas:
		for Partida in conRelacionFacturaxPartidas:
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
	newPago.RutaXML = jParams["RutaXML"]
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

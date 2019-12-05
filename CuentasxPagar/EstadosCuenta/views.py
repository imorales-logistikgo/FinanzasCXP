from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import RelacionFacturaProveedorxPartidas, FacturasxProveedor, PendientesEnviar, RelacionConceptoxProyecto
from EstadosCuenta.models import  View_FacturasxProveedor, CobrosxProveedor, CobrosxFacturasProveedor, RelacionCobrosFacturasxProveedor
from django.template.loader import render_to_string
from decimal import Decimal
import json, datetime


def EstadosdeCuenta(request):
	FacturasPendiente = View_FacturasxProveedor.objects.filter(Status = "Pendiente")
	FacturasAbonada = View_FacturasxProveedor.objects.filter(Status = "Abonada")
	result = FacturasPendiente | FacturasAbonada
	Folios = list()
	for Factura in result:
		FoliosCobro= ""
		for Cobro in RelacionCobrosFacturasxProveedor.objects.filter(IDFactura = Factura.IDFactura):
			FoliosCobro += Cobro.IDCobro.Folio + ", "
		FoliosCobro = FoliosCobro[:-2]
		Folios.append(FoliosCobro)
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
		FoliosCobro= ""
		for Cobro in RelacionCobrosFacturasxProveedor.objects.filter(IDFactura = Factura.IDFactura):
			FoliosCobro += Cobro.IDCobro.Folio + ", "
		FoliosCobro = FoliosCobro[:-2]
		Folios.append(FoliosCobro)
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



def SaveCobroxProveedor(request):
	jParams = json.loads(request.body.decode('utf-8'))
	newCobro = CobrosxProveedor()
	newCobro.FechaAlta = datetime.datetime.now()
	newCobro.Folio = jParams["Folio"]
	newCobro.Total = jParams["Total"]
	newCobro.FechaCobro = datetime.datetime.strptime(jParams["FechaCobro"],'%Y/%m/%d')
	newCobro.RutaXML = jParams["RutaXML"]
	newCobro.RutaPDF = jParams["RutaPDF"]
	newCobro.Comentarios = jParams["Comentarios"]
	newCobro.TipoCambio = jParams["TipoCambio"]
	newCobro.NombreCortoProveedor = jParams["Proveedor"]
	newCobro.save()
	return HttpResponse(newCobro.IDCobro)



def SaveCobroxFactura(request):
	jParams = json.loads(request.body.decode('utf-8'))
	for Cobro in jParams["arrCobros"]:
		newCobroxFactura = CobrosxFacturasProveedor()
		newCobroxFactura.Total = Cobro["Total"]
		newCobroxFactura.FechaAlta = datetime.datetime.now()
		newCobroxFactura.save()
		newRelacionCobroxFactura = RelacionCobrosFacturasxProveedor()
		newRelacionCobroxFactura.IDCobro = CobrosxProveedor.objects.get(IDCobro = jParams["IDCobro"])
		newRelacionCobroxFactura.IDCobroxFactura = CobrosxFacturasProveedor.objects.get(IDCobroxFactura = newCobroxFactura.IDCobroxFactura)
		Factura = FacturasxProveedor.objects.get(IDFactura = Cobro["IDFactura"])
		Factura.Saldo -= Decimal(Cobro["Total"])
		newRelacionCobroxFactura.IDFactura = Factura
		newRelacionCobroxFactura.IDUsuarioAlta = 1
		newRelacionCobroxFactura.IDProveedor = 1
		if Factura.Saldo == 0:
			Factura.Status = "Cobrada"
		else:
			Factura.Status = "Abonada"
		Factura.save()
		newRelacionCobroxFactura.save()
	return HttpResponse("")

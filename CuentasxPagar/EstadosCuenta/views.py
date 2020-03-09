from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import RelacionFacturaProveedorxPartidas, FacturasxProveedor, PendientesEnviar, RelacionConceptoxProyecto, Ext_PendienteEnviar_Costo
from EstadosCuenta.models import  View_FacturasxProveedor, PagosxProveedor, PagosxFacturas, RelacionPagosFacturasxProveedor
from usersadmon.models import Proveedor, AdmonUsuarios
from users.models import User
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from decimal import Decimal
from django.db.models import Q
import json, datetime, math
from django.contrib.auth.decorators import login_required

@login_required
def EstadosdeCuenta(request):
	if request.user.roles == 'Proveedor':
		 return render(request, '404.html')
	else:
		result = View_FacturasxProveedor.objects.filter(Q(Status = "PENDIENTE") | Q(Status = "ABONADA"))
		ListaFacturas = FacturasToList(result)
		Folios = list()
		for Factura in ListaFacturas:
			FoliosPago = ""
			for Pago in RelacionPagosFacturasxProveedor.objects.filter(IDFactura = Factura["IDFactura"]).select_related('IDPago'):
				if Pago.IDPago.Status != "CANCELADA":
					FoliosPago += Pago.IDPago.Folio + ", "
			FoliosPago = FoliosPago[:-2]
			Folios.append(FoliosPago)
		ContadoresPendientes, ContadoresAbonadas, ContadoresPagadas, ContadoresCanceladas = GetContadores()
		Proveedores = Proveedor.objects.all()
		return render(request, 'EstadosdeCuenta.html', {'Facturas': ListaFacturas, 'Proveedores': Proveedores, 'Folios': Folios, 'ContadoresPendientes': ContadoresPendientes, 'ContadoresAbonadas': ContadoresAbonadas, 'ContadoresPagadas': ContadoresPagadas, 'ContadoresCanceladas': ContadoresCanceladas, 'Rol': request.user.roles})



def GetContadores():
	AllFacturas = list(View_FacturasxProveedor.objects.values('Status').all())
	ContadoresPendientes = len(list(filter(lambda x: x["Status"] == "PENDIENTE", AllFacturas)))
	ContadoresAbonadas = len(list(filter(lambda x: x["Status"] == "ABONADA", AllFacturas)))
	ContadoresPagadas = len(list(filter(lambda x: x["Status"] == "PAGADA", AllFacturas)))
	ContadoresCanceladas = len(list(filter(lambda x: x["Status"] == "CANCELADA", AllFacturas)))
	return ContadoresPendientes, ContadoresAbonadas, ContadoresPagadas, ContadoresCanceladas



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
	ListaFacturas = FacturasToList(Facturas)
	Folios = list()
	for Factura in ListaFacturas:
		FoliosPago= ""
		for Pago in RelacionPagosFacturasxProveedor.objects.filter(IDFactura = Factura["IDFactura"]).select_related('IDPago'):
			FoliosPago += Pago.IDPago.Folio + ", "
		FoliosPago = FoliosPago[:-2]
		Folios.append(FoliosPago)
	htmlRes = render_to_string('TablaEstadosCuenta.html', {'Facturas': ListaFacturas, 'Folios': Folios}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def FacturasToList(Facturas):
	ListaFacturas = list()
	for Factura in Facturas:
		NuevaFactura = {}
		NuevaFactura["IDFactura"] = Factura.IDFactura
		NuevaFactura["Folio"] = Factura.Folio
		NuevaFactura["Proveedor"] = Factura.Proveedor
		NuevaFactura["FechaFactura"] = Factura.FechaFactura
		NuevaFactura["Subtotal"] = Factura.Subtotal
		NuevaFactura["IVA"] = Factura.IVA
		NuevaFactura["Retencion"] = Factura.Retencion
		NuevaFactura["Total"] = Factura.Total
		NuevaFactura["Saldo"] = Factura.Saldo
		NuevaFactura["FechaFactura"] = Factura.FechaFactura
		NuevaFactura["Moneda"] = Factura.Moneda
		NuevaFactura["Status"] = Factura.Status
		NuevaFactura["RutaXML"] = Factura.RutaXML
		NuevaFactura["IsAutorizada"] = Factura.IsAutorizada
		NuevaFactura["IDProveedor"] = Factura.IDProveedor
		ListaFacturas.append(NuevaFactura)
	return ListaFacturas



def CancelarFactura(request):
	IDFactura = json.loads(request.body.decode('utf-8'))["IDFactura"]
	conRelacionFacturaProveedorxPartidas = RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = IDFactura)
	if conRelacionFacturaProveedorxPartidas:
		conRelacionFacturaProveedorxPartidas[0].IDFacturaxProveedor.Status = 'CANCELADA'
		conRelacionFacturaProveedorxPartidas[0].IDFacturaxProveedor.IDUsuarioBaja = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
		conRelacionFacturaProveedorxPartidas[0].IDFacturaxProveedor.save()
		for Partida in conRelacionFacturaProveedorxPartidas:
			Partida.IDPartida.IsActiva = False
			Partida.IDPartida.FechaBaja = datetime.datetime.now()
			Ext_Costo = Ext_PendienteEnviar_Costo.objects.get(IDPendienteEnviar = Partida.IDPendienteEnviar)
			Ext_Costo.IsFacturaProveedor = False
			Ext_Costo.save()
			Partida.IDPartida.save()
	return HttpResponse("")




def GetDetallesFactura(request):
	ListaViajes = list()
	IDFactura = request.GET["IDFactura"]
	conRelacionFacturaProveedorxPartidas = RelacionFacturaProveedorxPartidas.objects.filter(IDFacturaxProveedor = IDFactura)
	if conRelacionFacturaProveedorxPartidas:
		for Partida in conRelacionFacturaProveedorxPartidas:
			Viaje = {}
			Pending = RelacionConceptoxProyecto.objects.get(IDPendienteEnviar = Partida.IDPendienteEnviar)
			Viaje["Folio"] = Pending.IDPendienteEnviar.Folio
			Viaje["FechaDescarga"] = Pending.IDPendienteEnviar.FechaDescarga
			Ext_Costo = Ext_PendienteEnviar_Costo.objects.get(IDPendienteEnviar = Pending.IDPendienteEnviar)
			Viaje["Subtotal"] = Ext_Costo.CostoSubtotal
			Viaje["IVA"] = Ext_Costo.CostoIVA
			Viaje["Retencion"] = Ext_Costo.CostoRetencion
			Viaje["Total"] = Ext_Costo.CostoTotal
			ListaViajes.append(Viaje)
	htmlRes = render_to_string('TablaDetallesFactura.html', {'Pendientes':ListaViajes}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def SavePagoxProveedor(request):
	jParams = json.loads(request.body.decode('utf-8'))
	newPago = PagosxProveedor()
	newPago.FechaAlta = datetime.datetime.now()
	newPago.Folio = jParams["Folio"]
	newPago.Total = jParams["Total"]
	newPago.FechaPago = datetime.datetime.strptime(jParams["FechaPago"],'%Y/%m/%d')
	if "RutaComprobante" in jParams:
		newPago.RutaComprobante = jParams["RutaComprobante"]
	newPago.Comentarios = jParams["Comentarios"]
	newPago.TipoCambio = jParams["TipoCambio"]
	newPago.NombreCortoProveedor = jParams["Proveedor"]
	newPago.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
	newPago.IDProveedor = jParams["IDProveedor"]
	newPago.save()
	return HttpResponse(newPago.IDPago)



def truncate(number, digits) -> Decimal:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def SavePagoxFactura(request):
	jParams = json.loads(request.body.decode('utf-8'))
	for Pago in jParams["arrPagos"]:
		newPagoxFactura = PagosxFacturas()
		newPagoxFactura.Total = Pago["Total"]
		newPagoxFactura.FechaAlta = datetime.datetime.now()
		newPagoxFactura.save()
		newRelacionPagoxFactura = RelacionPagosFacturasxProveedor()
		newRelacionPagoxFactura.IDPago = PagosxProveedor.objects.get(IDPago = jParams["IDPago"])
		newRelacionPagoxFactura.IDPagoxFactura = newPagoxFactura
		Factura = FacturasxProveedor.objects.get(IDFactura = Pago["IDFactura"])
		Factura.Saldo -= Decimal(Pago["Total"])
		newRelacionPagoxFactura.IDFactura = FacturasxProveedor.objects.get(IDFactura = Pago["IDFactura"])
		if truncate(float(Factura.Saldo), 2) == 0:
			Factura.Status = "PAGADA"
		else:
			Factura.Status = "ABONADA"
		print(Factura)
		Factura.save()
		newRelacionPagoxFactura.save()
		EnviarCorreoProveedor(IDPagoEmail = jParams["IDPago"])
	return HttpResponse("")



def ValidarFactura(request):
	IDFactura = json.loads(request.body.decode('utf-8'))["IDFactura"]
	Factura = FacturasxProveedor.objects.get(IDFactura = IDFactura)
	if Factura:
		Factura.IsAutorizada = True
		Factura.save()
	result = View_FacturasxProveedor.objects.filter(IDFactura = IDFactura)
	ListaFacturas = FacturasToList(result)
	Folios = list()
	for Fact in ListaFacturas:
		FoliosPago= ""
		for Pago in RelacionPagosFacturasxProveedor.objects.filter(IDFactura = Fact["IDFactura"]).select_related('IDPago'):
			FoliosPago += Pago.IDPago.Folio + ", "
		FoliosPago = FoliosPago[:-2]
		Folios.append(FoliosPago)
	htmlRes = render_to_string('TablaEstadosCuenta.html', {'Facturas':ListaFacturas, 'Folios': Folios}, request = request,)
	print(htmlRes)
	return JsonResponse({'htmlRes' : htmlRes})



def CheckFolioDuplicado(request):
	IsDuplicated = PagosxProveedor.objects.filter(Folio = request.GET["Folio"]).exclude(Status = "CANCELADA").exists()
	return JsonResponse({'IsDuplicated' : IsDuplicated})


def EnviarCorreoProveedor(IDPagoEmail):
	DatosPagoProveedor = PagosxProveedor.objects.get(IDPago = IDPagoEmail)
	CorreoProveedor = User.objects.get(IDTransportista = DatosPagoProveedor.IDProveedor)
	if CorreoProveedor.email != "":
		context={
			'nombre': DatosPagoProveedor.NombreCortoProveedor,
			'folio' : DatosPagoProveedor.Folio,
			'total' : DatosPagoProveedor.Total
		}
		template_name='email.html'
		html_content=render_to_string("CorreoProveedor.html", context)
		subject='Subir complementos de pago'
		from_email='noreply@logisti-k.com.mx'
		to='jfraga@logisti-k.com.mx'

		msg = EmailMessage(subject, html_content, from_email, [to])
		msg.content_subtype = "html"  # Main content is now text/html
		msg.send()

		return HttpResponse('Mail successfully sent')
	else:
		return HttpResponse('Correo no enviado, El Proveedor no tiene correo')




def GetDetallesPago(request):
	IDFactura = request.GET["IDFactura"]
	FacturasxPago = RelacionPagosFacturasxProveedor.objects.filter(IDFactura = IDFactura).select_related('IDPago').select_related('IDPagoxFactura')
	Facturas = list()
	for FacturaxPago in FacturasxPago:
		Pago = {}
		Pago["FolioPago"] = FacturaxPago.IDPago.Folio
		Pago["FechaPago"] = FacturaxPago.IDPago.FechaPago
		Pago["Total"] = FacturaxPago.IDPagoxFactura.Total
		Facturas.append(Pago)
	htmlRes = render_to_string('TablaDetallesPago.html', {'Facturas':Facturas}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})


def FixIDProveedor(request):
	Facturas = RelacionFacturaProveedorxPartidas.objects.all()
	for Factura in Facturas:
		IDProveedor = RelacionConceptoxProyecto.objects.filter(IDPendienteEnviar = Factura.IDPendienteEnviar.IDPendienteEnviar)[0].IDProveedor
		Fact = FacturasxProveedor.objects.get(IDFactura = Factura.IDFacturaxProveedor.IDFactura)
		Fact.IDProveedor = IDProveedor
		Fact.save()
	return HttpResponse('Done')

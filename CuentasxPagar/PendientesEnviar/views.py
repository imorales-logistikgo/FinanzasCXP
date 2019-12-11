from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import View_PendientesEnviarCxP, FacturasxProveedor, PartidaProveedor, RelacionFacturaProveedorxPartidas, PendientesEnviar
from django.core import serializers
from django.template.loader import render_to_string
import json, datetime



def GetPendientesEnviar(request):
	PendingToSend = View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s AND IsEvidenciaDigital = 1 AND IsEvidenciaFisica = 1 AND IsFacturaProveedor = 0 AND Moneda = %s", ['Finalizado', 'MXN'])
	ContadorTodos, ContadorPendientes, ContadorFinalizados, ContadorConEvidencias, ContadorSinEvidencias = GetContadores()
	return render(request, 'PendienteEnviar.html', {'pendientes':PendingToSend, 'contadorPendientes': ContadorPendientes, 'contadorFinalizados': ContadorFinalizados, 'contadorConEvidencias': ContadorConEvidencias, 'contadorSinEvidencias': ContadorSinEvidencias})



def GetContadores():
	ContadorTodos = len(list(View_PendientesEnviarCxP.objects.filter(IsFacturaProveedor = False)))
	ContadorPendientes = len(list(View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s", ['Pendiente'])))
	ContadorFinalizados = len(list(View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s", ['Finalizado'])))
	ContadorConEvidencias = len(list(View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE IsEvidenciaDigital = 1 AND IsEvidenciaFisica = 1")))
	ContadorSinEvidencias = ContadorTodos - ContadorConEvidencias
	return ContadorTodos, ContadorPendientes, ContadorFinalizados, ContadorConEvidencias, ContadorSinEvidencias


def GetPendientesByFilters(request):
	FechaDescargaDesde = request.GET["FechaDescargaDesde"]
	FechaDescargaHasta = request.GET["FechaDescargaHasta"]
	Proveedor = json.loads(request.GET["Proveedor"])
	Status = json.loads(request.GET["Status"])
	Moneda = request.GET["Moneda"]
	if not Status:
		QueryStatus = ""
	else:
		QueryStatus = "Status IN ({}) AND ".format(','.join(['%s' for _ in range(len(Status))]))
	if not Proveedor:
		QueryClientes = ""
	else:
		QueryClientes = "NombreProveedor IN ({}) AND ".format(','.join(['%s' for _ in range(len(Proveedor))]))
	QueryFecha = "FechaDescarga BETWEEN %s AND %s AND "
	QueryMoneda = "Moneda = %s "
	FinalQuery = "SELECT * FROM View_PendientesEnviarCxP WHERE " + QueryStatus + QueryClientes + QueryFecha + QueryMoneda + "AND IsFacturaProveedor = 0"
	params = Status + Proveedor + [FechaDescargaDesde, FechaDescargaHasta] + [Moneda]
	PendingToSend = View_PendientesEnviarCxP.objects.raw(FinalQuery,params)
	htmlRes = render_to_string('TablaPendientes.html', {'pendientes':PendingToSend}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def SaveFacturaxProveedor(request):
	jParams = json.loads(request.body.decode('utf-8'))
	newFactura = FacturasxProveedor()
	newFactura.Folio = jParams["FolioFactura"]
	newFactura.NombreCortoProveedor = jParams["Proveedor"]
	newFactura.FechaFactura = datetime.datetime.strptime(jParams["FechaFactura"],'%Y/%m/%d')
	newFactura.FechaRevision = datetime.datetime.strptime(jParams["FechaRevision"],'%Y/%m/%d')
	newFactura.FechaVencimiento = datetime.datetime.strptime(jParams["FechaVencimiento"],'%Y/%m/%d')
	newFactura.Moneda = jParams["Moneda"]
	newFactura.Subtotal = jParams["SubTotal"]
	newFactura.IVA = jParams["IVA"]
	newFactura.Total = jParams["Total"]
	newFactura.Saldo = jParams["Total"]
	newFactura.Retencion = jParams["Retencion"]
	newFactura.TipoCambio = jParams["TipoCambio"]
	newFactura.Comentarios = jParams["Comentarios"]
	newFactura.RutaXML = jParams["RutaXML"]
	newFactura.RutaPDF = jParams["RutaPDF"]
	newFactura.save()
	return HttpResponse(newFactura.IDFactura)



def SavePartidasxFactura(request):
	jParams = json.loads(request.body.decode('utf-8'))
	for IDConcepto in jParams["arrConceptos"]:
		Viaje = View_PendientesEnviarCxP.objects.get(IDConcepto = IDConcepto)
		newPartida = PartidaProveedor()
		newPartida.FechaAlta = datetime.datetime.now()
		newPartida.Subtotal = Viaje.CostoSubtotal
		newPartida.IVA = Viaje.CostoIVA
		newPartida.Retencion = Viaje.CostoRetencion
		newPartida.Total = Viaje.CostoTotal
		newPartida.save()
		newRelacionFacturaxPartida = RelacionFacturaProveedorxPartidas()
		newRelacionFacturaxPartida.IDFacturaxProveedor = FacturasxProveedor.objects.get(IDFactura = jParams["IDFactura"])
		newRelacionFacturaxPartida.IDPartida = newPartida
		newRelacionFacturaxPartida.IDConcepto = IDConcepto
		newRelacionFacturaxPartida.IDUsuarioAlta = 1
		newRelacionFacturaxPartida.IDUsuarioBaja = 1
		newRelacionFacturaxPartida.save()
		Viaje.IDPendienteEnviar.IsFacturaProveedor = True
		Viaje.IDPendienteEnviar.save()
	PendingToSend = View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s AND IsEvidenciaDigital = 1 AND IsEvidenciaFisica = 1 AND IsFacturaProveedor = 0", ['Finalizado'])
	htmlRes = render_to_string('TablaPendientes.html', {'pendientes':PendingToSend}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})

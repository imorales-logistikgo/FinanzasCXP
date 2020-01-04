from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import View_PendientesEnviarCxP, FacturasxProveedor, PartidaProveedor, RelacionFacturaProveedorxPartidas, PendientesEnviar, Ext_PendienteEnviar_Costo
from django.core import serializers
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
@login_required

def GetPendientesEnviar(request):
	PendingToSend = View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s AND IsEvidenciaDigital = 1 AND IsEvidenciaFisica = 1 AND IsFacturaProveedor = 0 AND Moneda = %s", ['Finalizado', 'MXN'])
	ContadorTodos, ContadorPendientes, ContadorFinalizados, ContadorConEvidencias, ContadorSinEvidencias = GetContadores()
	ListPendientes = PendientesToList(PendingToSend)
	return render(request, 'PendienteEnviar.html', {'pendientes':ListPendientes, 'contadorPendientes': ContadorPendientes, 'contadorFinalizados': ContadorFinalizados, 'contadorConEvidencias': ContadorConEvidencias, 'contadorSinEvidencias': ContadorSinEvidencias})



def PendientesToList(PendingToSend):
	ListPendientes = list()
	for Pend in PendingToSend:
		Viaje = {}
		Viaje["Folio"] = Pend.Folio
		Viaje["NombreProveedor"] = Pend.NombreProveedor
		Viaje["FechaDescarga"] = Pend.FechaDescarga
		Viaje["Subtotal"] = Pend.Subtotal
		Viaje["IVA"] = Pend.IVA
		Viaje["Retencion"] = Pend.Retencion
		Viaje["Total"] = Pend.Total
		Viaje["Moneda"] = Pend.Moneda
		Viaje["Status"] = Pend.Status
		Viaje["IDConcepto"] = Pend.IDConcepto
		Viaje["IDPendienteEnviar"] = Pend.IDPendienteEnviar
		Viaje["IsEvidenciaFisica"] = Pend.IsEvidenciaFisica
		Viaje["IsEvidenciaDigital"] = Pend.IsEvidenciaDigital
		ListPendientes.append(Viaje)
	return ListPendientes



def GetContadores():
	AllPending = list(View_PendientesEnviarCxP.objects.values("IsFacturaProveedor", "Status", "IsEvidenciaDigital", "IsEvidenciaFisica").all())
	ContadorTodos = len(list(filter(lambda x: x["IsFacturaProveedor"] == False, AllPending)))
	ContadorPendientes = len(list(filter(lambda x: x["Status"] == "Pendiente", AllPending)))
	ContadorFinalizados = len(list(filter(lambda x: x["Status"] == "Finalizado", AllPending)))
	ContadorConEvidencias = len(list(filter(lambda x: x["IsEvidenciaFisica"] == True and x["IsEvidenciaDigital"] == True, AllPending)))
	ContadorSinEvidencias = ContadorTodos - ContadorConEvidencias
	return ContadorTodos, ContadorPendientes, ContadorFinalizados, ContadorConEvidencias, ContadorSinEvidencias


def GetPendientesByFilters(request):
	Proveedor = json.loads(request.GET["Proveedor"])
	Status = json.loads(request.GET["Status"])
	Moneda = request.GET["Moneda"]
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		PendingToSend = View_PendientesEnviarCxP.objects.filter(FechaDescarga__month__in = arrMonth, FechaDescarga__year = Year, IsFacturaProveedor = False)
	else:
		PendingToSend = View_PendientesEnviarCxP.objects.filter(FechaDescarga__range = [datetime.datetime.strptime(request.GET["FechaDescargaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaDescargaHasta"],'%m/%d/%Y')], IsFacturaProveedor = False)
	if Status:
		if "Con evidencias" in Status:
			PendingToSend = PendingToSend.filter(IsEvidenciaDigital = True, IsEvidenciaFisica = True)
			if len(Status) > 1:
				PendingToSend = PendingToSend.filter(Status__in = Status)
		else:
			PendingToSend = PendingToSend.filter(Status__in = Status)
	if Proveedor:
		PendingToSend = PendingToSend.filter(NombreProveedor__in = Proveedor)
	PendingToSend = PendingToSend.filter(Moneda = Moneda)
	ListPendientes = PendientesToList(PendingToSend)
	htmlRes = render_to_string('TablaPendientes.html', {'pendientes':ListPendientes}, request = request,)
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
	for IDPendienteEnviar in jParams["arrPendientes"]:
		Viaje = View_PendientesEnviarCxP.objects.get(IDPendienteEnviar = IDPendienteEnviar)
		newPartida = PartidaProveedor()
		newPartida.FechaAlta = datetime.datetime.now()
		newPartida.Subtotal = Viaje.Subtotal
		newPartida.IVA = Viaje.IVA
		newPartida.Retencion = Viaje.Retencion
		newPartida.Total = Viaje.Total
		newPartida.save()
		newRelacionFacturaxPartida = RelacionFacturaProveedorxPartidas()
		newRelacionFacturaxPartida.IDFacturaxProveedor = FacturasxProveedor.objects.get(IDFactura = jParams["IDFactura"])
		newRelacionFacturaxPartida.IDPartida = newPartida
		newRelacionFacturaxPartida.IDPendienteEnviar = PendientesEnviar.objects.get(IDPendienteEnviar = IDPendienteEnviar)
		newRelacionFacturaxPartida.IDUsuarioAlta = 1
		newRelacionFacturaxPartida.IDUsuarioBaja = 1
		newRelacionFacturaxPartida.save()
		Ext_Costo = Ext_PendienteEnviar_Costo.objects.get(IDPendienteEnviar = Viaje.IDPendienteEnviar)
		Ext_Costo.IsFacturaProveedor = True
		Ext_Costo.save()
	PendingToSend = View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s AND IsEvidenciaDigital = 1 AND IsEvidenciaFisica = 1 AND IsFacturaProveedor = 0", ['Finalizado'])
	htmlRes = render_to_string('TablaPendientes.html', {'pendientes':PendingToSend}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def CheckFolioDuplicado(request):
	IsDuplicated = FacturasxProveedor.objects.filter(Folio = request.GET["Folio"]).exists()
	return JsonResponse({'IsDuplicated' : IsDuplicated})



def FindFolioProveedor(request):
	Folio = request.GET["Folio"]
	try:
		PendienteEnviar = View_PendientesEnviarCxP.objects.get(Folio = Folio, IsFacturaProveedor = False)
		return JsonResponse({'Found' : True, 'Folio' : PendienteEnviar.Folio, 'Proveedor' : PendienteEnviar.NombreProveedor, 'FechaDescarga' : PendienteEnviar.FechaDescarga, 'IDPendienteEnviar' : PendienteEnviar.IDPendienteEnviar, 'Subtotal': PendienteEnviar.Subtotal, 'IVA': PendienteEnviar.IVA, 'Retencion': PendienteEnviar.Retencion, 'Total' : PendienteEnviar.Total})
	except:
		return JsonResponse({'Found' : False})

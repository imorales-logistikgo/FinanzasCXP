from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import View_PendientesEnviarCxP, FacturasxProveedor, PartidaProveedor, RelacionFacturaProveedorxPartidas, PendientesEnviar, Ext_PendienteEnviar_Costo
from usersadmon.models import Proveedor, AdmonUsuarios
from users import models as User
from django.core import serializers
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required
def GetPendientesEnviar(request):
	#PendingToSend = View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s AND IsEvidenciaDigital = 1 AND IsEvidenciaFisica = 1 AND IsFacturaProveedor = 0 AND Moneda = %s", ['FINALIZADO', 'MXN'])
	PendingToSend = View_PendientesEnviarCxP.objects.filter(Status = 'FINALIZADO', IsEvidenciaDigital = 1, IsEvidenciaFisica = 1, IsFacturaProveedor = 0, Moneda = 'MXN', FechaDescarga__month = datetime.datetime.now().month, FechaDescarga__year = datetime.datetime.now().year)
	ContadorTodos, ContadorPendientes, ContadorFinalizados, ContadorConEvidencias, ContadorSinEvidencias = GetContadores()
	Proveedores = Proveedor.objects.all()
	ListPendientes = PendientesToList(PendingToSend)
	return render(request, 'PendienteEnviar.html', {'Pendientes':ListPendientes, 'Proveedores': Proveedores, 'contadorPendientes': ContadorPendientes, 'contadorFinalizados': ContadorFinalizados, 'contadorConEvidencias': ContadorConEvidencias, 'contadorSinEvidencias': ContadorSinEvidencias, 'Rol': request.user.roles, 'IDUsuraio_': request.user.idusuario})


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
		Viaje["IDProveedor"] = Pend.IDProveedor
		ListPendientes.append(Viaje)
	return ListPendientes



def GetContadores():
	AllPending = list(View_PendientesEnviarCxP.objects.values("IsFacturaProveedor", "Status", "IsEvidenciaDigital", "IsEvidenciaFisica").all())
	ContadorTodos = len(list(filter(lambda x: x["IsFacturaProveedor"] == False, AllPending)))
	ContadorPendientes = len(list(filter(lambda x: x["Status"] == "PENDIENTE", AllPending)))
	ContadorFinalizados = len(list(filter(lambda x: x["Status"] == "FINALIZADO", AllPending)))
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
	htmlRes = render_to_string('TablaPendientes.html', {'Pendientes':ListPendientes}, request = request,)
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
	newFactura.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
	newFactura.IDProveedor =  jParams["IDProveedor"]
	newFactura.TotalXML = jParams["TotalXML"]
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
	PendingToSend = View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s AND IsEvidenciaDigital = 1 AND IsEvidenciaFisica = 1 AND IsFacturaProveedor = 0", ['FINALIZADO'])
	htmlRes = render_to_string('TablaPendientes.html', {'Pendientes':PendingToSend}, request = request,)
	return JsonResponse({'htmlRes' : htmlRes})



def CheckFolioDuplicado(request):
	IsDuplicated = FacturasxProveedor.objects.filter(Folio = request.GET["Folio"]).exclude(Status = "CANCELADA").exists()
	return JsonResponse({'IsDuplicated' : IsDuplicated})



def FindFolioProveedor(request):
	Folio = request.GET["Folio"]
	try:
		PendienteEnviar = View_PendientesEnviarCxP.objects.filter(Folio = Folio, IsFacturaProveedor = False, IsEvidenciaFisica = True, IsEvidenciaDigital = True, IDProveedor = request.user.IDTransportista, Status= 'FINALIZADO').last()
		if PendienteEnviar.IsControlDesk != 0:
			return JsonResponse({'Found' : True, 'Folio' : PendienteEnviar.Folio, 'Proveedor' : PendienteEnviar.NombreProveedor, 'FechaDescarga' : PendienteEnviar.FechaDescarga, 'IDPendienteEnviar' : PendienteEnviar.IDPendienteEnviar, 'IDProveedor' : PendienteEnviar.IDProveedor, 'Subtotal': PendienteEnviar.Subtotal, 'IVA': PendienteEnviar.IVA, 'Retencion': PendienteEnviar.Retencion, 'Total' : PendienteEnviar.Total})
		else:
			return JsonResponse({'Found' : False})
	except:
		return JsonResponse({'Found' : False})


def GetSerieProveedor(request):
	try:
		IDProveedor = request.GET["IDProveedor"]
		getSerie = Proveedor.objects.get(IDTransportista = IDProveedor)
		Serie = getSerie.Serie
		IsAmericano = getSerie.IsAmericano
		return JsonResponse({'Serie' : Serie, 'IsAmericano': IsAmericano})
	except:
		return HttpResponse(status=500)


def GetProveedorByID(request):
	IDProveedor = request.Get["IDProveedor"]
	Proveedor = Proveedor.objects.get(IDTransportista = IDProveedor)
	IsAmericano = Proveedor.IsAmericano
	return JsonResponse({'IsAmericano': IsAmericano})


def CrearUsuariosTranportistas(request):
#editar un usuario

	#usuarios = User.User.objects.filter()
	#FoliosSuccess = list()
	#FoliosNoSuccess = list()
	#for a in usuarios:
	#	try:
	#		usu = AdmonUsuarios.objects.get(idusuario = a.idusuario)
	#		if usu.idusuario == a.idusuario and usu.nombreusuario == a.username:
	#			FoliosSuccess.append(a.id)
	#		else:
	#			FoliosNoSuccess.append(a.id)
	#	except:
	#		pass
	#findFolio = User.User.objects.filter(id = 20)
	#for correctoID in findFolio:
	#	try:
	#		findNombreUsuario = AdmonUsuarios.objects.get(nombreusuario = correctoID.username)
	#		getRSTransportista =  Proveedor.objects.get(IDTransportista = correctoID.IDTransportista)
	#		correctoID.idusuario = findNombreUsuario.idusuario
	#		if getRSTransportista.RFC == correctoID.username:
	#			correctoID.name = getRSTransportista.RazonSocial
	#		correctoID.save()
	#	except:
	#		pass
	#print(FoliosNoSuccess)

#fin editar usuario

#dar de alta un usuario

	#Proveedores = Proveedor.objects.exclude(Q(RFC__isnull=True)| Q(RFC='')|Q(RFC=None))

	Proveedores = Proveedor.objects.filter(RFC='TSU750725AS5')
	# for prov in Proveedores:
	# 	try:
	# 		oldUser = AdmonUsuarios.objects.get(nombreusuario = prov.RFC)
	# 	except AdmonUsuarios.DoesNotExist:
	# 		newUser = AdmonUsuarios()
	# 		newUser.nombre = prov.RazonSocial
	# 		newUser.nombreusuario = prov.RFC
	# 		newUser.correo = prov.Correo
	# 		newUser.fechacambiocontrasena = datetime.datetime.now()
	# 		newUser.hasbytes = 0
	# 		newUser.saltbytes = 0
	# 		newUser.periodo = 365
	# 		newUser.statusreg = "ACTIVO"
	# 		newUser.apepaterno = ""
	# 		newUser .apematerno = ""
	# 		newUser.save()
	# 		prov.IDUsuarioAcceso = newUser.idusuario
	# 		prov.save()
	# 		try:
	# 			DjangoUser = User.User.objects.get(username=prov.RFC)
	# 			DjangoUser.IDTransportista = prov.IDTransportista
	# 			DjangoUser.idusuario = newUser.idusuario
	# 		except User.User.DoesNotExist:
	# 			user = User.User(username=prov.RFC)
	# 			user.name = newUser.nombre+" "+newUser.apepaterno+" "+newUser.apematerno
	# 			user.email = newUser.correo
	# 			user.idusuario = newUser.idusuario
	# 			user.is_staff = True
	# 			user.roles = "Proveedor"
	# 			user.IDTransportista = prov.IDTransportista
	# 			user.save()

	# fin dar de alta un usuario

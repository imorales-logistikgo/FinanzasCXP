from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from PendientesEnviar.models import View_PendientesEnviarCxP, FacturasxProveedor, PartidaProveedor, RelacionFacturaProveedorxPartidas, PendientesEnviar, Ext_PendienteEnviar_Costo
from usersadmon.models import Proveedor, AdmonUsuarios
from CartaNoAdeudo.models import CartaNoAdeudoTransportistas
from XD_Viajes.models import XD_Viajes
from bkg_viajes.models import Bro_Viajes
from users import models as User
from django.core import serializers
from django.template.loader import render_to_string
import json, datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect
from xml.dom import minidom
import urllib
import re
import calendar
from CartaNoAdeudo.views import MesCartaNoAdeudo


@login_required
def GetPendientesEnviar(request):
    #PendingToSend = View_PendientesEnviarCxP.objects.raw("SELECT * FROM View_PendientesEnviarCxP WHERE Status = %s AND IsEvidenciaDigital = 1 AND IsEvidenciaFisica = 1 AND IsFacturaProveedor = 0 AND Moneda = %s", ['FINALIZADO', 'MXN'])
    if request.user.roles == 'MesaControl':
        return redirect('EvidenciasProveedor')
    elif request.user.roles == 'Contabilidad':
        return redirect('ReportePagos')
    # elif request.user.roles == 'Proveedor':
    # 	return redirect('Actualizacion')
    else:
        PendingToSend = View_PendientesEnviarCxP.objects.filter(Status = 'FINALIZADO', IsEvidenciaDigital = 1, IsEvidenciaFisica = 1, IsFacturaProveedor = 0, Moneda = 'MXN', FechaDescarga__month = datetime.datetime.now().month, FechaDescarga__year = datetime.datetime.now().year)
        ContadorTodos, ContadorPendientes, ContadorFinalizados, ContadorConEvidencias, ContadorSinEvidencias = GetContadores()
        DiasDelMesbloquear = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]-1
        RangoBloquearFacturas = DiasDelMesbloquear <= datetime.datetime.now().day <=  calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
        DiaDelMesbloquearAlert = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]-2
        DiaDelMesMotrarAlerta = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1] - 7
        RangoDiasAlerta = DiaDelMesMotrarAlerta <= datetime.datetime.now().day <= calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
        MesAlerta = MesEnAlertaBloquearFacturas(datetime.datetime.now())
        DiaAlerta = DiaEnAlertaBloquearFacturas(calendar.weekday(datetime.datetime.now().year, datetime.datetime.now().month, DiaDelMesbloquearAlert))
        DiaAMostrarEnAlerta = DiaAlerta + " " + str(DiaDelMesbloquearAlert)
        DiaAlertaCarta = DiaEnAlertaBloquearFacturas(calendar.weekday(datetime.datetime.now().year, datetime.datetime.now().month, 20))
        DiaAMostrarEnAlertaCarta = DiaAlertaCarta + " " +"20"

        GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
            IDTransportista=request.user.IDTransportista, MesCartaNoAdeudo=MesEnAlertaCarta(datetime.datetime.now()), Status='APROBADA')

        if request.user.roles == 'Proveedor' and datetime.datetime.now().day > 20 and GetTotalViajesEn1Mes(request.user.IDTransportista,1):
            GetFechaAltaTransportista = Proveedor.objects.get(IDTransportista = request.user.IDTransportista)
            if CartaNoAdeudoTransportistas.objects.filter(IDTransportista=request.user.IDTransportista, MesCartaNoAdeudo=MesEnAlertaCarta(datetime.datetime.now()), Status='APROBADA').exists():
                if GetFechaAltaTransportista.FechaAlta is None:
                    BloquearFacturasCarta = True
                else:
                    BloquearFacturasCarta = True if GetFechaAltaTransportista.FechaAlta.month != datetime.datetime.now().month and GetFechaAltaTransportista.FechaAlta.year != datetime.datetime.now().year else False
            else:
                BloquearFacturasCarta = False if GetLastCartaUpload.MesCartaNoAdeudo == MesCartaNoAdeudo(
                    datetime.datetime.now()) and GetLastCartaUpload.Status == "APROBADA" else True
            MesAlertaMotivoBloqueo = MesEnAlertaCarta(datetime.datetime.now())
        elif request.user.roles == 'Proveedor' and GetTotalViajesEn1Mes(request.user.IDTransportista,2):
            GetLastCartaUpload2 = CartaNoAdeudoTransportistas.objects.filter(
                IDTransportista=request.user.IDTransportista, MesCartaNoAdeudo=MesCartaConAdeudo(datetime.datetime.now()), Status='APROBADA')
            if not CartaNoAdeudoTransportistas.objects.filter(IDTransportista=request.user.IDTransportista, MesCartaNoAdeudo=MesCartaConAdeudo(datetime.datetime.now()), Status='APROBADA').exists():
                BloquearFacturasCarta = True
            else:
                if GetLastCartaUpload2.MesCartaNoAdeudo == MesCartaConAdeudo(datetime.datetime.now()) and GetLastCartaUpload.Status == "APROBADA":
                    BloquearFacturasCarta = False
                else :
                    BloquearFacturasCarta = True
            MesAlertaMotivoBloqueo = MesCartaConAdeudo(datetime.datetime.now())
        else:
            BloquearFacturasCarta = False
            MesAlertaMotivoBloqueo = "null"

        Proveedores = Proveedor.objects.all()
        ListPendientes = PendientesToList(PendingToSend)
        bloquearLinkCarta = 1 <= datetime.datetime.now().day <= 20
        FechaCorteCarta = str(calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month-1)[1]) + " de " + MesEnAlertaCarta(datetime.datetime.now())
    return render(request, 'PendienteEnviar.html',
                  {'FechaCorteCarta': FechaCorteCarta, 'bloquearLinkCarta': bloquearLinkCarta,
                   'DiaAMostrarEnAlertaCarta': DiaAMostrarEnAlertaCarta, 'Pendientes': ListPendientes,
                   'Proveedores': Proveedores, 'contadorPendientes': ContadorPendientes,
                   'contadorFinalizados': ContadorFinalizados, 'contadorConEvidencias': ContadorConEvidencias,
                   'contadorSinEvidencias': ContadorSinEvidencias, 'Rol': request.user.roles,
                   'IDUsuraio_': request.user.idusuario, 'BloquearFacturas': RangoBloquearFacturas,
                   'MostrarAlerta': RangoDiasAlerta, 'MesAlerta': MesAlerta, 'DiaShowAlert': DiaAMostrarEnAlerta,
                   'BloquearFacturasCarta': BloquearFacturasCarta, 'MesAlertaMotivoBloqueo':MesAlertaMotivoBloqueo})


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
    newFactura.TipoCambio = jParams["TipoCambio"] if jParams["Moneda"] == "MXN" else GetTipoCambioXML(jParams["RutaXML"]) if jParams["Moneda"] == "USD" else jParams["TipoCambio"]
    newFactura.Comentarios = jParams["Comentarios"]
    newFactura.RutaXML = jParams["RutaXML"]
    newFactura.RutaPDF = jParams["RutaPDF"]
    newFactura.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
    newFactura.IDProveedor =  jParams["IDProveedor"]
    newFactura.TotalXML = jParams["TotalXML"]
    newFactura.UUID = jParams["UUID"] if request.user.idusuario != 3126 else ""
    newFactura.Status = 'DEPURADO' if(jParams["Estado"] == 'YU') else 'PENDIENTE'
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
            return JsonResponse({'Found' : True, 'Folio' : PendienteEnviar.Folio, 'Proveedor' : PendienteEnviar.NombreProveedor, 'FechaDescarga' : PendienteEnviar.FechaDescarga, 'IDPendienteEnviar' : PendienteEnviar.IDPendienteEnviar, 'IDProveedor' : PendienteEnviar.IDProveedor, 'Subtotal': PendienteEnviar.Subtotal, 'IVA': PendienteEnviar.IVA, 'Retencion': PendienteEnviar.Retencion, 'Total' : PendienteEnviar.Total, 'Moneda' : PendienteEnviar.Moneda})
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
    IDProveedor = request.GET["IDProveedor"]
    Proveedor1 = Proveedor.objects.get(IDTransportista = IDProveedor)
    IsAmericano = Proveedor1.IsAmericano
    return JsonResponse({'IsAmericano': IsAmericano})

def Actualizacion(request):
    return render(request, 'update.html')

def GetValidacionesCFDIAndOther(request):
    File = request.GET["XML"]
    try:
        ListOfTagData = list()
        xml = urllib.request.urlopen(File)
        XMLReadyToRead = minidom.parse(xml)
        TagComprobante = XMLReadyToRead.getElementsByTagName('cfdi:Comprobante')
        FormaPago = TagComprobante[0].attributes['FormaPago'].value
        SameFormaPago = True if FormaPago == '99' else False
        ListOfTagData.append(SameFormaPago)
        TipoDeComprobante = TagComprobante[0].attributes['TipoDeComprobante'].value
        SameTipoDeComprobante = True if TipoDeComprobante == "I" else False
        ListOfTagData.append(SameTipoDeComprobante)
        MetodoPago = TagComprobante[0].attributes['MetodoPago'].value
        SameMetodoPago = True if MetodoPago == 'PPD' else False
        ListOfTagData.append(SameMetodoPago)
        TagRFCReceptor = XMLReadyToRead.getElementsByTagName('cfdi:Receptor')
        UsoCFDI = TagRFCReceptor[0].attributes['UsoCFDI'].value
        SameUsoCFDI = True if UsoCFDI == "G03" else False
        ListOfTagData.append(SameUsoCFDI)
        RFCReceptor = TagRFCReceptor[0].attributes['Rfc'].value
        SameRFC = True if RFCReceptor == "LKM021004ERA" else False
        ListOfTagData.append(SameRFC)
        ResponseTagData = True if False not in ListOfTagData else False
        return JsonResponse({"Response": ResponseTagData})
    except Exception as e:
        return JsonResponse({"Response": False})


def GetTipoCambioXML(File):
    xml = urllib.request.urlopen(File)
    XMLReadyToRead = minidom.parse(xml)
    TagComprobante = XMLReadyToRead.getElementsByTagName('cfdi:Comprobante')
    TipoCambio = TagComprobante[0].attributes['TipoCambio'].value
    return TipoCambio

def GetFolioViajeXML(request):
    try:
        if request.user.IDTransportista != 1241:
            XMLFile = request.GET["XML"]
            FolioToCheck = request.GET["Folio"]
            xml = urllib.request.urlopen(XMLFile)
            XMLToRead = minidom.parse(xml)
            TagConcepto = XMLToRead.getElementsByTagName('cfdi:Concepto')
            FolioViaje = TagConcepto[0].attributes['Descripcion'].value
            FindFolioInXML = re.search(FolioToCheck, FolioViaje)
            if FindFolioInXML is not None:
                indexstart = FindFolioInXML.start()
                indexend = FindFolioInXML.end()
                FolioInXML = FolioViaje[indexstart:indexend]
                SameFolio = True if FolioInXML == FolioToCheck else False
            else:
                TagNoIdentificacion = XMLToRead.getElementsByTagName('cfdi:Concepto')
                if 'NoIdentificacion' in TagNoIdentificacion[0].attributes:
                    FolioViajeInTagNoIdentificacion = TagNoIdentificacion[0].attributes['NoIdentificacion'].value
                    FindFolioInTagNoIdentificacion = re.search(FolioToCheck, FolioViajeInTagNoIdentificacion)
                    if FindFolioInTagNoIdentificacion is not None:
                        indexstart = FindFolioInTagNoIdentificacion.start()
                        indexend = FindFolioInTagNoIdentificacion.end()
                        FolioInXML = FolioViajeInTagNoIdentificacion[indexstart:indexend]
                        SameFolio = True if FolioInXML == FolioToCheck else False
                    else:
                        TagUnidad = XMLToRead.getElementsByTagName('cfdi:Concepto')
                        FolioViajeInTagUnidad = TagUnidad[0].attributes['Unidad'].value
                        FindFolioInTagUnidad = re.search(FolioToCheck, FolioViajeInTagUnidad)
                        if FindFolioInTagUnidad is not None:
                            indexstart = FindFolioInTagUnidad.start()
                            indexend = FindFolioInTagUnidad.end()
                            FolioInXML = FolioViajeInTagUnidad[indexstart:indexend]
                            SameFolio = True if FolioInXML == FolioToCheck else False
                        else:
                            SameFolio = GetFolioInTagParte(XMLToRead,FolioToCheck)
                else:
                    TagUnidad = XMLToRead.getElementsByTagName('cfdi:Concepto')
                    FolioViajeInTagUnidad = TagUnidad[0].attributes['Unidad'].value
                    FindFolioInTagUnidad = re.search(FolioToCheck, FolioViajeInTagUnidad)
                    if FindFolioInTagUnidad is not None:
                        indexstart = FindFolioInTagUnidad.start()
                        indexend = FindFolioInTagUnidad.end()
                        FolioInXML = FolioViajeInTagUnidad[indexstart:indexend]
                        SameFolio = True if FolioInXML == FolioToCheck else False
                    else:
                        SameFolio = GetFolioInTagParte(XMLToRead,FolioToCheck)
        else:
            SameFolio = True
        return JsonResponse({"Folio":SameFolio})
    except Exception as e:
        print(e)
        return JsonResponse({"Folio":False})


def GetFolioInTagParte(XMLToRead,FolioToCheck):
    try:
        if XMLToRead.getElementsByTagName('cfdi:Parte') != []:
            TagParte = XMLToRead.getElementsByTagName('cfdi:Parte')
            FolioViajeInTagParte = TagParte[0].attributes['Descripcion'].value
            FindFolioInTagParte = re.search(FolioToCheck, FolioViajeInTagParte)
            if FindFolioInTagParte is not None:
                indexstart = FindFolioInTagParte.start()
                indexend = FindFolioInTagParte.end()
                FolioInXML = FolioViajeInTagParte[indexstart:indexend]
                SameFolio = True if FolioInXML == FolioToCheck else False
            else:
                TagParte1 = XMLToRead.getElementsByTagName('cfdi:Parte')
                FolioViajeInTagParteNoIdentificacion = TagParte1[0].attributes['NoIdentificacion'].value
                FindFolioInTagParteNoIdentificacion = re.search(FolioToCheck, FolioViajeInTagParteNoIdentificacion)
                if FindFolioInTagParteNoIdentificacion is not None:
                    indexstart = FindFolioInTagParteNoIdentificacion.start()
                    indexend = FindFolioInTagParteNoIdentificacion.end()
                    FolioInXML = FolioViajeInTagParteNoIdentificacion[indexstart:indexend]
                    SameFolio = True if FolioInXML == FolioToCheck else False
                else:
                    SameFolio = False
        else:
            SameFolio = False
        print(SameFolio)
        return SameFolio
    except Exception as e:
        print(e)
        SameFolio = False
        return SameFolio


def MesEnAlertaBloquearFacturas(Fecha):
    months = (
        "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
        "Noviembre","Diciembre")
    Mes = months[Fecha.month - 1]
    return Mes

def DiaEnAlertaBloquearFacturas(Dia):
    Dyas = ("Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo")
    dia = Dyas[Dia]
    return dia

def MesEnAlertaCarta(Fecha):
    months = (
        "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
        "Noviembre","Diciembre")
    Mes = months[Fecha.month - 2]
    return Mes

def MesCartaConAdeudo(Fecha):
    months = (
        "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
        "Noviembre","Diciembre")
    Mes1 = months[Fecha.month - 3]
    return Mes1



def GetTotalViajesEn1Mes(IDTransportista, RestarMes):
    CountViajesEnXD = XD_Viajes.objects.exclude(Status='CANCELADO').filter(IDTransportista=IDTransportista,
                                               FechaAlta__month=datetime.datetime.now().month - RestarMes).count()
    CountViajesEnBKG = Bro_Viajes.objects.exclude(StatusProceso = 'CANCELADO').filter(IDTransportista=IDTransportista,
                                                 FechaAlta__month=datetime.datetime.now().month - RestarMes).count()
    TieneViajes = True if CountViajesEnXD >= 1 and CountViajesEnBKG >= 1 else False
    return TieneViajes



# def CrearUsuariosTranportistas(request):
# #editar un usuario
#
# 	#usuarios = User.User.objects.filter()
# 	#FoliosSuccess = list()
# 	#FoliosNoSuccess = list()
# 	#for a in usuarios:
# 	#	try:
# 	#		usu = AdmonUsuarios.objects.get(idusuario = a.idusuario)
# 	#		if usu.idusuario == a.idusuario and usu.nombreusuario == a.username:
# 	#			FoliosSuccess.append(a.id)
# 	#		else:
# 	#			FoliosNoSuccess.append(a.id)
# 	#	except:
# 	#		pass
# 	#findFolio = User.User.objects.filter(id = 20)
# 	#for correctoID in findFolio:
# 	#	try:
# 	#		findNombreUsuario = AdmonUsuarios.objects.get(nombreusuario = correctoID.username)
# 	#		getRSTransportista =  Proveedor.objects.get(IDTransportista = correctoID.IDTransportista)
# 	#		correctoID.idusuario = findNombreUsuario.idusuario
# 	#		if getRSTransportista.RFC == correctoID.username:
# 	#			correctoID.name = getRSTransportista.RazonSocial
# 	#		correctoID.save()
# 	#	except:
# 	#		pass
# 	#print(FoliosNoSuccess)
#
# #fin editar usuario
#
#dar de alta un usuario

    # Proveedores = Proveedor.objects.exclude(Q(RFC__isnull=True)| Q(RFC='')|Q(RFC=None))

    # Proveedores = Proveedor.objects.filter(RFC='GAHN820801L68')
    # for prov in Proveedores:
    #     try:
    #         oldUser = AdmonUsuarios.objects.get(nombreusuario = prov.RFC)
    #     except AdmonUsuarios.DoesNotExist:
    #         newUser = AdmonUsuarios()
    #         newUser.nombre = prov.RazonSocial
    #         newUser.nombreusuario = prov.RFC
    #         newUser.correo = prov.Correo
    #         newUser.fechacambiocontrasena = datetime.datetime.now()
    #         newUser.hasbytes = 0
    #         newUser.saltbytes = 0
    #         newUser.periodo = 365
    #         newUser.statusreg = "ACTIVO"
    #         newUser.apepaterno = ""
    #         newUser .apematerno = ""
    #         newUser.save()
    #         prov.IDUsuarioAcceso = newUser.idusuario
    #         prov.save()
    #         try:
    #             DjangoUser = User.User.objects.get(username=prov.RFC)
    #             DjangoUser.IDTransportista = prov.IDTransportista
    #             DjangoUser.idusuario = newUser.idusuario
    #         except User.User.DoesNotExist:
    #             user = User.User(username=prov.RFC)
    #             user.name = newUser.nombre+" "+newUser.apepaterno+" "+newUser.apematerno
    #             user.email = newUser.correo
    #             user.idusuario = newUser.idusuario
    #             user.is_staff = True
    #             user.roles = "Proveedor"
    #             user.IDTransportista = prov.IDTransportista
    #             user.save()

    # fin dar de alta un usuario

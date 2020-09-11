import uuid
from io import BytesIO

from azure.storage.blob import BlobClient
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from io import BytesIO
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from XD_Viajes.models import XD_Viajes, XD_PedidosxViajes, XD_Pedidos, XD_AccesoriosxViajes, XD_EvidenciasxPedido, XD_EvidenciasxViaje
from PendientesEnviar.models import PendientesEnviar, RelacionConceptoxProyecto
from usersadmon.models import AdmonUsuarios,Proveedor, View_EvidenciasCxP
from bkg_viajes.models import Bro_Viajes, Bro_EvidenciasxViaje
import json, datetime
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json
from itertools import chain
import requests
from django.template.loader import render_to_string

@login_required
def EvidenciasProveedor(request):
    if request.user.roles == 'MesaControl':
        EvidenciasxAprobar = XD_Viajes.objects.filter(Status = 'FINALIZADO', FechaDespacho__month = datetime.datetime.now().month, FechaDespacho__year = datetime.datetime.now().year).exclude(Status = 'CANCELADO')
        EvidenciasxAprobarBKG = Bro_Viajes.objects.filter(StatusProceso = 'FINALIZADO', FechaDescarga__month = datetime.datetime.now().month, FechaDescarga__year = datetime.datetime.now().year).exclude(StatusProceso = 'CANCELADO')
        Evidencias = chain(EvidenciasxAprobar, EvidenciasxAprobarBKG)
        SinEvidenciaDigitalXD = XD_Viajes.objects.filter(IsEvidenciaPedidos = False).count()
        SinEvidenciaDigitalBKG = Bro_Viajes.objects.filter(IsEvidenciasDigitales = False).count()
        SinEvidenciaDigital = SinEvidenciaDigitalXD+SinEvidenciaDigitalBKG
        Proveedores = Proveedor.objects.all()
        return render(request, 'EvidenciasProveedor.html', {'EvidenciasxAprobar': Evidencias, 'EvidenciaDigital': SinEvidenciaDigital, 'Proveedores':Proveedores})
    elif request.user.roles == 'Proveedor':
        # SinEvidenciaDigital = XD_Viajes.objects.filter(IsEvidencia = False).count()
        # SinEvidenciaFisica = XD_Viajes.objects.filter(IsEvidenciaFisica = False).count()
        return render(request, 'EvidenciasProveedor.html')
    elif request.user.roles == 'users':
        Evidencias = View_EvidenciasCxP.objects.all()
        # EvidenciasxAprobarBKG = Bro_Viajes.objects.filter(StatusProceso='FINALIZADO', IsEvidenciasDigitales=1, FechaDescarga__month = datetime.datetime.now().month, FechaDescarga__year = datetime.datetime.now().year)
        # Evidencias = EvidenciasxAprobarXD.union(EvidenciasxAprobarBKG)
        # Evidencias = chain(EvidenciasxAprobarXD, EvidenciasxAprobarBKG)
        return render(request, 'EvidenciasProveedor.html', {'Evidencias': Evidencias})


def FindFolioProveedorE(request):
    Folio = request.GET["Folio"]
    try:
        arrFoliosEvidencias = list()
        if 'XDD' in Folio:
            XDFolio = XD_Viajes.objects.exclude(Status = 'CANCELADO').get(Folio = Folio, Status = 'FINALIZADO', IDTransportista = request.user.IDTransportista)
            if XDFolio.TipoViaje == 'CUSTODIA':
                GetEvidenciaxManiobra = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje = XDFolio.XD_IDViaje, Tipo = 'EVCUSTODIAF')
                if GetEvidenciaxManiobra:
                    for DataEvidenciaxManiobra in GetEvidenciaxManiobra:
                        newDelivery = {}
                        newDelivery['XD_IDPedido'] = DataEvidenciaxManiobra.IDEvidenciaxViaje
                        newDelivery['Delivery'] = XDFolio.Folio+"-"+DataEvidenciaxManiobra.Titulo
                        newDelivery['IDViaje'] = DataEvidenciaxManiobra.IDXD_Viaje
                        newDelivery['TipoEvidencia'] = 'Custodia'
                        newDelivery['RutaArchivo'] = '' if(DataEvidenciaxManiobra.IsEnviada and DataEvidenciaxManiobra.IsRechazada ) else DataEvidenciaxManiobra.RutaArchivo
                        newDelivery['Status'] = 'Rechazada' if(DataEvidenciaxManiobra.IsEnviada and DataEvidenciaxManiobra.IsRechazada) else 'Aprobada' if(DataEvidenciaxManiobra.IsValidada) else  "Enviada" if (DataEvidenciaxManiobra.IsEnviada and not DataEvidenciaxManiobra.IsRechazada and not DataEvidenciaxManiobra.IsValidada) else "Otro"
                        newDelivery['ComentarioRechazo'] = DataEvidenciaxManiobra.ComentarioRechazo
                        arrFoliosEvidencias.append(newDelivery)
                else:
                    for i in range(2):
                        newDelivery = {}
                        newDelivery['XD_IDPedido'] = XDFolio.XD_IDViaje
                        newDelivery['Delivery'] = XDFolio.Folio+"-"+"FOLIO" if(i==0) else XDFolio.Folio+"-"+"CORREO"
                        newDelivery['IDViaje'] = XDFolio.XD_IDViaje
                        newDelivery['TipoEvidencia'] = 'Custodia'
                        newDelivery['RutaArchivo'] = ''
                        newDelivery['Status'] = 'Pendiente'
                        newDelivery['ComentarioRechazo'] = ""
                        arrFoliosEvidencias.append(newDelivery)
            else:
                GetDelivery = XD_PedidosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje)#, StatusPedido = 'ENTREGADO')
                if GetDelivery:
                    for Delivery in GetDelivery:
                        if len(XD_EvidenciasxPedido.objects.filter(IDXD_Pedido = Delivery.XD_IDPedido.XD_IDPedido, XD_IDViaje = Delivery.XD_IDViaje.XD_IDViaje)) >= 1:
                            TieneEvidencia = XD_EvidenciasxPedido.objects.get(IDXD_Pedido = Delivery.XD_IDPedido.XD_IDPedido, XD_IDViaje = Delivery.XD_IDViaje.XD_IDViaje)
                            newDelivery = {}
                            newDelivery['XD_IDPedido'] = Delivery.XD_IDPedido.XD_IDPedido
                            newDelivery['Delivery'] = Delivery.XD_IDPedido.Delivery.replace(".","")
                            newDelivery['IDViaje'] = Delivery.XD_IDViaje.XD_IDViaje
                            newDelivery['TipoEvidencia'] = 'Pedido'
                            newDelivery['RutaArchivo'] = '' if(TieneEvidencia.IsEnviada and TieneEvidencia.IsRechazada ) else TieneEvidencia.RutaArchivo
                            newDelivery['Status'] = 'Rechazada' if(TieneEvidencia.IsEnviada and TieneEvidencia.IsRechazada) else 'Aprobada' if(TieneEvidencia.IsValidada) else  "Enviada" if (TieneEvidencia.IsEnviada and not TieneEvidencia.IsRechazada and not TieneEvidencia.IsValidada) else "Otro"
                            newDelivery['ComentarioRechazo'] = TieneEvidencia.ComentarioRechazo
                            arrFoliosEvidencias.append(newDelivery)
                        else:
                            newDelivery = {}
                            newDelivery['XD_IDPedido'] = Delivery.XD_IDPedido.XD_IDPedido
                            newDelivery['Delivery'] = Delivery.XD_IDPedido.Delivery.replace(".","")
                            newDelivery['IDViaje'] = Delivery.XD_IDViaje.XD_IDViaje
                            newDelivery['TipoEvidencia'] = 'Pedido'
                            newDelivery['RutaArchivo'] = "" if(GetDelivery[0].IsEvidenciaPedidoxViaje == 1 or GetDelivery[0].IsEvidenciaFisicaPedidoxViaje == 1) else ""
                            newDelivery['Status'] = 'Otro' if(GetDelivery[0].IsEvidenciaPedidoxViaje == 1 or GetDelivery[0].IsEvidenciaFisicaPedidoxViaje == 1) else 'Pendiente'
                            newDelivery['ComentarioRechazo'] = ""
                            arrFoliosEvidencias.append(newDelivery)
            for Maniobras in XD_AccesoriosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje, Descripcion__in = ('Maniobras de descarga', 'Maniobras de carga')):
                if Maniobras:
                    GetManiobras = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje = Maniobras.XD_IDViaje, Titulo__in = ('Maniobras de descarga', 'Maniobras de carga'), Tipo="MESA CONTROL")
                    if len(GetManiobras) == 0:
                        newDelivery = {}
                        newDelivery['XD_IDPedido'] = Maniobras.XD_IDAccesorioxViaje #if(len(GetManiobras) == 0) else Maniobras.XD_IDAccesorioxViaje if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else GetEachManiobra.IDEvidenciaxViaje
                        newDelivery['Delivery'] = Maniobras.Descripcion #if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else Maniobras.Descripcion if(len(GetManiobras) == 0) else GetEachManiobra.Titulo
                        newDelivery['IDViaje'] = Maniobras.XD_IDViaje #if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else Maniobras.XD_IDViaje if(len(GetManiobras) == 0) else GetEachManiobra.IDXD_Viaje
                        newDelivery['TipoEvidencia'] = 'Maniobras'
                        newDelivery['RutaArchivo'] = '' #if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else GetEachManiobra.RutaArchivo if (GetEachManiobra.IsEnviada and not GetEachManiobra.IsRechazada and not GetEachManiobra.IsValidada) else GetEachManiobra.RutaArchivo
                        newDelivery['Status'] = 'Pendiente' #if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else 'Aprobada' if(GetEachManiobra.IsEnviada and GetEachManiobra.IsValidada) else 'Pendiente' if len(GetManiobras) == 0 else "Enviada" if (GetEachManiobra.IsEnviada and not GetEachManiobra.IsRechazada and not GetEachManiobra.IsValidada) else "Otro"
                        newDelivery['ComentarioRechazo'] = ""
                        arrFoliosEvidencias.append(newDelivery)
                    else:
                        for GetEachManiobra in GetManiobras:
                            newDelivery = {}
                            newDelivery['XD_IDPedido'] =GetEachManiobra.IDEvidenciaxViaje
                            newDelivery['Delivery'] = Maniobras.Descripcion if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else Maniobras.Descripcion if(len(GetManiobras) == 0) else GetEachManiobra.Titulo
                            newDelivery['IDViaje'] = GetEachManiobra.IDXD_Viaje
                            newDelivery['TipoEvidencia'] = 'Maniobras'
                            newDelivery['RutaArchivo'] = '' if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else GetEachManiobra.RutaArchivo if (GetEachManiobra.IsEnviada and not GetEachManiobra.IsRechazada and not GetEachManiobra.IsValidada) else GetEachManiobra.RutaArchivo
                            newDelivery['Status'] = 'Rechazada' if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else 'Aprobada' if(GetEachManiobra.IsEnviada and GetEachManiobra.IsValidada) else 'Pendiente' if len(GetManiobras) == 0 else "Enviada" if (GetEachManiobra.IsEnviada and not GetEachManiobra.IsRechazada and not GetEachManiobra.IsValidada) else "Otro"
                            newDelivery['ComentarioRechazo'] = GetEachManiobra.ComentarioRechazo
                            arrFoliosEvidencias.append(newDelivery)
        elif 'FTL' in Folio:
            GetEviBKG = FindFolioEvidenciaBGK(Folio, request.user.IDTransportista)
            for i in GetEviBKG['ListaEvidencias']:
                arrFoliosEvidencias.append(i)
        return JsonResponse({'Found': True, 'Folios': arrFoliosEvidencias})
    except Exception as e:
        print(e)
        return JsonResponse({'Found': False})


def SaveEvidencias(request):
    jParams = json.loads(request.body.decode('utf-8'))
    try:
        for Evidencias in jParams['arrEvidencias']:
            with transaction.atomic(using='XD_ViajesDB'):
                TituloEvidencia = 'Maniobras de descarga' if(Evidencias['Titulo'] == 'Maniobrasdedescarga') else 'Maniobras de carga' if(Evidencias['Titulo'] == 'Maniobrasdecarga') else ""
                if Evidencias['Status'] == 'Rechazada':
                    if Evidencias['TipoEvidencia'] == 'BKG':
                        SaveEvidenciasxBKG = Bro_EvidenciasxViaje.objects.get(IDBro_EvidenciaxViaje = Evidencias['IDPedido'])
                        SaveEvidenciasxBKG.FechaCaptura = datetime.datetime.now()
                        SaveEvidenciasxBKG.NombreArchivo = Evidencias['NombreArchivo']
                        SaveEvidenciasxBKG.RutaArchivo = Evidencias['Evidencia']
                        SaveEvidenciasxBKG.IsRechazada = False
                        SaveEvidenciasxBKG.IsEnviada = True
                        SaveEvidenciasxBKG.IsRemplazada = True
                        SaveEvidenciasxBKG.IDUsuarioAlta = request.user.idusuario
                        SaveEvidenciasxBKG.save()
                    else:
                        SaveEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDXD_Pedido = Evidencias['IDPedido'], XD_IDViaje = Evidencias['IDViaje']) if(Evidencias['TipoEvidencia'] == 'Pedido') else XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje =Evidencias['IDPedido'], IDXD_Viaje = Evidencias['IDViaje']) if(Evidencias['TipoEvidencia'] == 'Maniobras' or 'Custodia') else ""
                        SaveEvidenciaxPedido.FechaCaptura = datetime.datetime.now()
                        SaveEvidenciaxPedido.NombreArchivo = Evidencias['NombreArchivo']
                        SaveEvidenciaxPedido.RutaArchivo = Evidencias['Evidencia']
                        SaveEvidenciaxPedido.IsRechazada = False
                        SaveEvidenciaxPedido.IsEnviada = True
                        SaveEvidenciaxPedido.IsRemplazada = True
                        SaveEvidenciaxPedido.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
                        SaveEvidenciaxPedido.save()
                    return HttpResponse(status = 200)
                elif Evidencias['Status'] == 'Pendiente':
                    if Evidencias['TipoEvidencia'] == 'BKG':
                        SaveEvidenciaBKG = Bro_EvidenciasxViaje()
                        SaveEvidenciaBKG.IDBro_Viaje = Bro_Viajes.objects.get(IDBro_Viaje = Evidencias['IDViaje'])
                        SaveEvidenciaBKG.FechaCaptura = datetime.datetime.now()
                        SaveEvidenciaBKG.Titulo = Evidencias['Titulo']
                        SaveEvidenciaBKG.Tipo = 'EVIDENCIA'
                        SaveEvidenciaBKG.NombreArchivo = Evidencias['NombreArchivo']
                        SaveEvidenciaBKG.RutaArchivo = Evidencias['Evidencia']
                        SaveEvidenciaBKG.IsEnviada = True
                        SaveEvidenciaBKG.IDUsuarioAlta = request.user.idusuario
                        SaveEvidenciaBKG.save()
                    else:
                        if Evidencias['TipoEvidencia'] == 'Custodia':
                            TituloCustodia = GetTituloForCustodia(Evidencias['Titulo'])
                        SaveEvidenciaxPedido = XD_EvidenciasxPedido() if(Evidencias['TipoEvidencia'] == 'Pedido') else XD_EvidenciasxViaje() if(Evidencias['TipoEvidencia'] == 'Maniobras' or 'Custodia') else ""
                        SaveEvidenciaxPedido.IDXD_Pedido = Evidencias['IDPedido'] if(Evidencias['TipoEvidencia'] == 'Pedido') else None
                        if Evidencias['TipoEvidencia'] == 'Pedido':
                            SaveEvidenciaxPedido.XD_IDViaje = Evidencias['IDViaje']
                        elif Evidencias['TipoEvidencia'] == 'Maniobras' or 'Custodia':
                            SaveEvidenciaxPedido.IDXD_Viaje =   Evidencias['IDViaje']
                        SaveEvidenciaxPedido.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
                        SaveEvidenciaxPedido.FechaCaptura = datetime.datetime.now()
                        SaveEvidenciaxPedido.Titulo = 'EVIDENCIA1' if(Evidencias['TipoEvidencia'] == 'Pedido') else TituloEvidencia if(Evidencias['TipoEvidencia'] == 'Maniobras') else TituloCustodia if(Evidencias['TipoEvidencia'] == 'Custodia') else ""
                        SaveEvidenciaxPedido.Tipo = 'EVIDENCIA' if(Evidencias['TipoEvidencia'] == 'Pedido') else 'MESA CONTROL' if(Evidencias['TipoEvidencia'] == 'Maniobras') else "EVCUSTODIAF" if(Evidencias['TipoEvidencia'] == 'Custodia') else ""
                        SaveEvidenciaxPedido.NombreArchivo = Evidencias['NombreArchivo']
                        SaveEvidenciaxPedido.RutaArchivo = Evidencias['Evidencia']
                        SaveEvidenciaxPedido.Observaciones = ''
                        SaveEvidenciaxPedido.IsEnviada = True
                        SaveEvidenciaxPedido.save()
                # elif Evidencias['TipoEvidencia'] == 'BKG':
                #     print("yes")
                #     SaveEvidenciaBKG = Bro_EvidenciasxViaje()
                #     SaveEvidenciaBKG.IDBro_Viaje = Bro_Viajes.objects.get(IDBro_Viaje = Evidencias['IDViaje'])
                #     SaveEvidenciaBKG.FechaCaptura = datetime.datetime.now()
                #     SaveEvidenciaBKG.Titulo = Evidencias['Titulo']
                #     SaveEvidenciaBKG.Tipo = 'EVIDENCIA'
                #     SaveEvidenciaBKG.NombreArchivo = Evidencias['NombreArchivo']
                #     SaveEvidenciaBKG.RutaArchivo = Evidencias['Evidencia']
                #     SaveEvidenciaBKG.IsEnviada = True
                #     SaveEvidenciaBKG.save()
        return HttpResponse(status = 200)
    except Exception as e:
            print(e)
            transaction.rollback(using='XD_ViajesDB')
            return HttpResponse(status = 500)



def GetEvidenciasMesaControl(request):
    IDViaje = request.GET["XD_IDViaje"]
    print(IDViaje)
    Folio = request.GET["Folio"]
    ListEvidencias = list()
    try:
        if "FTL" in Folio:
            # print(Bro_Viajes.objects.filter(IDBro_Viaje = IDViaje))
            GetEvidenciasValidarBGK = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje = IDViaje, IsEnviada = 1, IsRechazada = 0, IsValidada = 0)
            for EvidenciaBKG in GetEvidenciasValidarBGK:
                AddEvidencia = {}
                AddEvidencia['IDEvidencia'] = EvidenciaBKG.IDBro_EvidenciaxViaje
                AddEvidencia['URLEvidencia'] = EvidenciaBKG.RutaArchivo
                AddEvidencia['Delivery'] = EvidenciaBKG.Titulo
                AddEvidencia['TipoEvidencia'] = 'BKG'
                AddEvidencia['IDViaje'] = EvidenciaBKG.IDBro_Viaje.IDBro_Viaje
                ListEvidencias.append(AddEvidencia)
        else:
            GetIDPedidos = XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje).values('XD_IDPedido')
            for GetPedidos in GetIDPedidos:
                GetDelivery = XD_Pedidos.objects.get(XD_IDPedido = GetPedidos['XD_IDPedido'])
                GetEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDXD_Pedido = GetPedidos['XD_IDPedido'], XD_IDViaje = IDViaje)
                if GetEvidenciaxPedido.IsEnviada and not GetEvidenciaxPedido.IsValidada and not GetEvidenciaxPedido.IsRechazada:
                    AddEvidencia = {}
                    AddEvidencia['IDEvidencia'] = GetEvidenciaxPedido.IDEvidenciaxPedido
                    AddEvidencia['URLEvidencia'] = GetEvidenciaxPedido.RutaArchivo
                    AddEvidencia['Delivery'] = GetDelivery.Delivery.replace('.',"")
                    AddEvidencia['TipoEvidencia'] = 'Pedido'
                    AddEvidencia['IDViaje'] = GetEvidenciaxPedido.XD_IDViaje
                    ListEvidencias.append(AddEvidencia)
            GetEvidenciasxViaje = XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga','Maniobras de carga'), Tipo = 'MESA CONTROL') | Q(IDXD_Viaje = IDViaje, Tipo = 'EVCUSTODIAF'))
            # ListEvi = EvidenciasToList(GetEvidenciasxViaje)
            for Maniobras in GetEvidenciasxViaje: #ListEvi:
                if Maniobras.Titulo and not Maniobras.IsValidada and not Maniobras.IsRechazada:
                    AddManiobras = {}
                    AddManiobras["IDEvidencia"] = Maniobras.IDEvidenciaxViaje
                    AddManiobras['URLEvidencia'] = Maniobras.RutaArchivo
                    AddManiobras['Delivery'] = Maniobras.Titulo
                    AddManiobras['TipoEvidencia'] = "Custodia" if(Maniobras.Tipo == 'EVCUSTODIAF') else "Maniobras"
                    AddManiobras['IDViaje'] = Maniobras.IDXD_Viaje
                    ListEvidencias.append(AddManiobras)
                # if Maniobras['Titulo'] and not Maniobras['IsValidada'] and not Maniobras['IsRechazada']:
                #     AddManiobras = {}
                #     AddManiobras["IDEvidencia"] = Maniobras['IDEvidenciaxViaje']
                #     AddManiobras['URLEvidencia'] = Maniobras['RutaArchivo']
                #     AddManiobras['Delivery'] = Maniobras['Titulo']
                #     AddManiobras['TipoEvidencia'] = Maniobras['TipoEvidencia']
                #     AddManiobras['IDViaje'] = Maniobras['IDXD_Viaje']
                #     ListEvidencias.append(AddManiobras)
        return JsonResponse({'Evidencias': ListEvidencias})
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

def EvidenciasToList(Evidencia):
    ListEvi= list()
    for NewEvidencia in Evidencia:
        Delivery = {}
        Delivery["IDEvidenciaxViaje"] = NewEvidencia.IDEvidenciaxViaje
        Delivery["IDXD_Viaje"] = NewEvidencia.IDXD_Viaje
        Delivery["RutaArchivo"] =NewEvidencia.RutaArchivo
        Delivery["Titulo"] = NewEvidencia.Titulo
        Delivery["IsValidada"] = NewEvidencia.IsValidada
        Delivery["IsRechazada"] = NewEvidencia.IsRechazada
        Delivery["IsEnviada"] = NewEvidencia.IsEnviada
        Delivery["TipoEvidencia"] = 'Maniobras'
        ListEvi.append(Delivery)
    return ListEvi

def SaveAprobarEvidencia(request):
    jParams = json.loads(request.body.decode('utf-8'))
    try:
        with transaction.atomic(using = 'XD_ViajesDB'):
            with transaction.atomic(using='bkg_viajesDB'):
                with transaction.atomic(using='users'):
                    if jParams['TipoEvidencia'] == 'Pedido':
                        SaveEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDEvidenciaxPedido = jParams['IDSaveEvidencia'])
                        SaveEvidenciaxPedido.IsValidada = True
                        SaveEvidenciaxPedido.Observaciones = jParams['Comentarios']
                        SaveEvidenciaxPedido.FechaValidacion = datetime.datetime.now()
                        SaveEvidenciaxPedido.save()
                        SaveBanderaPedidoxviaje = XD_PedidosxViajes.objects.get(XD_IDPedido = SaveEvidenciaxPedido.IDXD_Pedido, XD_IDViaje = SaveEvidenciaxPedido.XD_IDViaje)
                        SaveBanderaPedidoxviaje.IsEvidenciaPedidoxViaje = True
                        SaveBanderaPedidoxviaje.IDUsuarioEvDigital = request.user.idusuario
                        SaveBanderaPedidoxviaje.save()
                        IsXpress = XD_Viajes.objects.get(XD_IDViaje=SaveEvidenciaxPedido.XD_IDViaje) #IsViajeXpress(SaveEvidenciaxPedido.IDXD_Pedido, SaveEvidenciaxPedido.XD_IDViaje)
                        if IsXpress.TipoViaje == "XPRESS":
                            GetAllIDEvidenciasPedidos = XD_PedidosxViajes.objects.filter(XD_IDPedido = SaveEvidenciaxPedido.IDXD_Pedido)
                            for SaveEachPedidoPE in  GetAllIDEvidenciasPedidos:
                                GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto = SaveEachPedidoPE.XD_IDPedido.XD_IDPedido).values('IDPendienteEnviar')
                                for VerificarTipoConcepto in GetIDPendientesEnviar:
                                    SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar = VerificarTipoConcepto['IDPendienteEnviar'])
                                    if SaveBanderaPendientesEnviar.TipoConcepto == 'PEDIDO':
                                        SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                                        SaveBanderaPendientesEnviar.save()
                        SaveXD_EDigital = EvidenciaDigitalCompleta("",SaveBanderaPedidoxviaje.XD_IDViaje.XD_IDViaje)
                        if SaveXD_EDigital:
                            SaveXD_EDigital = XD_Viajes.objects.get(XD_IDViaje = SaveBanderaPedidoxviaje.XD_IDViaje.XD_IDViaje)
                            SaveXD_EDigital.IsEvidenciaPedidos = True
                            SaveXD_EDigital.FechaEvidenciaDigital = datetime.datetime.now()
                            SaveXD_EDigital.save()
                            VerificarEvidenciaT1yT2 = GetAllEvidecesDigitalsT1yT2(SaveBanderaPedidoxviaje.XD_IDViaje.XD_IDViaje)
                            if VerificarEvidenciaT1yT2:
                                VerificarValidacionesEvidencias = VerificarSaveViajePE(SaveBanderaPedidoxviaje.XD_IDPedido.XD_IDPedido)
                                for EachViaje in VerificarValidacionesEvidencias:
                                    GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto = EachViaje).values('IDPendienteEnviar')
                                    for VerificarTipoConcepto in GetIDPendientesEnviar:
                                        SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar = VerificarTipoConcepto['IDPendienteEnviar'])
                                        if SaveBanderaPendientesEnviar.TipoConcepto == 'VIAJE':
                                            SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                                            SaveBanderaPendientesEnviar.save()
                    if jParams['TipoEvidencia'] == 'Maniobras' or jParams['TipoEvidencia'] == 'Custodia':
                        SaveEvidenciaxManiobra = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje = jParams['IDSaveEvidencia'])
                        SaveEvidenciaxManiobra.IsValidada = True
                        SaveEvidenciaxManiobra.Observaciones = jParams['Comentarios']
                        SaveEvidenciaxManiobra.FechaValidacion = datetime.datetime.now()
                        SaveEvidenciaxManiobra.IDUsuarioEvDigital = request.user.idusuario
                        SaveEvidenciaxManiobra.save()
                            # if jParams['TipoEvidencia'] == 'Custodia': #las maniobras no se guardan la evidencia digital como bandera en cxp o cxc
                            #     GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto = SaveEvidenciaxManiobra.IDXD_Viaje)
                            #     SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar = GetIDPendientesEnviar[0].IDPendienteEnviar.IDPendienteEnviar)
                            #     SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                            #     SaveBanderaPendientesEnviar.save()
                        SaveXD_EDigital = EvidenciaDigitalCompleta("",SaveEvidenciaxManiobra.IDXD_Viaje)
                        if SaveXD_EDigital:
                            SaveXD_EDigital1 = XD_Viajes.objects.get(XD_IDViaje = SaveEvidenciaxManiobra.IDXD_Viaje)
                            SaveXD_EDigital1.IsEvidenciaPedidos = True
                            SaveXD_EDigital1.FechaEvidenciaDigital = datetime.datetime.now()
                            SaveXD_EDigital1.save()
                            if jParams['TipoEvidencia'] == 'Custodia':
                                GetIDPendientesEnviar1 = RelacionConceptoxProyecto.objects.filter(IDConcepto=SaveXD_EDigital1.XD_IDViaje)
                                for TC in GetIDPendientesEnviar1:
                                    SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar=TC.IDPendienteEnviar.IDPendienteEnviar)
                                    if SaveBanderaPendientesEnviar.TipoConcepto == 'VIAJE':
                                        SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                                        SaveBanderaPendientesEnviar.save()
                            elif jParams['TipoEvidencia'] == 'Maniobras':
                                GetIDPendientesEnviar1 = RelacionConceptoxProyecto.objects.filter(IDConcepto=SaveXD_EDigital1.XD_IDViaje)
                                for TC in GetIDPendientesEnviar1:
                                    SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar = TC.IDPendienteEnviar.IDPendienteEnviar)
                                    if SaveBanderaPendientesEnviar.TipoConcepto == 'VIAJE':
                                        SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                                        SaveBanderaPendientesEnviar.save()
                    if jParams['TipoEvidencia'] == 'BKG':
                        SaveAprobarEvidencia = Bro_EvidenciasxViaje.objects.get(IDBro_EvidenciaxViaje = jParams['IDSaveEvidencia'])
                        SaveAprobarEvidencia.IsValidada = True
                        SaveAprobarEvidencia.Observaciones = jParams['Comentarios']
                        SaveAprobarEvidencia.FechaValidacion = datetime.datetime.now()
                        SaveAprobarEvidencia.IDUsuarioEvDigital = request.user.idusuario
                        SaveAprobarEvidencia.save()
                        SaveEvidenciaDigitalViaje = EvidenciaDigitalCompletaBKG("",SaveAprobarEvidencia.IDBro_Viaje.IDBro_Viaje)
                        if SaveEvidenciaDigitalViaje:
                            GetEvDViaje = Bro_Viajes.objects.get(IDBro_Viaje = SaveAprobarEvidencia.IDBro_Viaje.IDBro_Viaje)
                            GetEvDViaje.IsEvidenciasDigitales = True
                            GetEvDViaje.FechaRecEviDigitales = datetime.datetime.now()
                            GetEvDViaje.save()
                            GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.get(IDConcepto = SaveAprobarEvidencia.IDBro_Viaje.IDBro_Viaje)
                            GetEvDAdmon = PendientesEnviar.objects.get(IDPendienteEnviar = str(GetIDPendientesEnviar.IDPendienteEnviar))
                            GetEvDAdmon.IsEvidenciaDigital = True
                            GetEvDAdmon.save()
                    return HttpResponse(status = 200)
    except Exception as e:
        print(e)
        transaction.rollback(using = 'XD_ViajesDB')
        transaction.rollback(using = 'bkg_viajesDB')
        transaction.rollback(using = 'users')
        return HttpResponse(status = 500)


def RechazarEvidencias(request):
    jParams = json.loads(request.body.decode('utf-8'))
    if jParams['TipoEvidencia'] == 'Pedido':
        RechazarEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDEvidenciaxPedido = jParams['IDRechazarEvidencia'])
        RechazarEvidenciaxPedido.IsRechazada = True
        RechazarEvidenciaxPedido.Observaciones = jParams['Comentarios']
        RechazarEvidenciaxPedido.ComentarioRechazo = jParams['ComentarioRechazo']
        RechazarEvidenciaxPedido.IDUsuarioRechaza = request.user.idusuario
        RechazarEvidenciaxPedido.FechaRechazo = datetime.datetime.now()
        RechazarEvidenciaxPedido.save()
    elif jParams['TipoEvidencia'] == 'Maniobras' or jParams['TipoEvidencia'] == 'Custodia':
        RechazarEvidenciaManiobra = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje = jParams['IDRechazarEvidencia'])
        RechazarEvidenciaManiobra.IsRechazada = True
        RechazarEvidenciaManiobra.Observaciones = jParams['Comentarios']
        RechazarEvidenciaManiobra.ComentarioRechazo = jParams['ComentarioRechazo']
        RechazarEvidenciaManiobra.IDUsuarioRechaza = request.user.idusuario
        RechazarEvidenciaManiobra.FechaRechazo = datetime.datetime.now()
        RechazarEvidenciaManiobra.save()
    elif jParams['TipoEvidencia'] == "BKG":
        RechazarEvidenciaBKG = Bro_EvidenciasxViaje.objects.get(IDBro_EvidenciaxViaje = jParams['IDRechazarEvidencia'])
        RechazarEvidenciaBKG.IsRechazada = True
        RechazarEvidenciaBKG.Observaciones = jParams['Comentarios']
        RechazarEvidenciaBKG.ComentarioRechazo = jParams['ComentarioRechazo']
        RechazarEvidenciaBKG.IDUsuarioRechaza = request.user.idusuario
        RechazarEvidenciaBKG.FechaRechazo = datetime.datetime.now()
        RechazarEvidenciaBKG.save()
    return HttpResponse("")


def ValidarEvidenciaXD_Viajea(IDViaje):
    AllEvidencesPedidosTrue = XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje)
    listEvidenciasBool = list()
    for a in AllEvidencesPedidosTrue:
        listEvidenciasBool.append(a.IsEvidenciaPedidoxViaje,)
        listEvidenciasBool.append(a.IsEvidenciaFisicaPedidoxViaje,)
    AllEvidencesManiobrasTrue = XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga','Maniobras de carga'), Tipo="MESA CONTROL") | Q(IDXD_Viaje = IDViaje, Tipo = 'EVCUSTODIAF'))
    if len(AllEvidencesManiobrasTrue) >=1:
        for b in AllEvidencesManiobrasTrue:
            listEvidenciasBool.append(b.IsEvidenciaFisicaAprobada) if(b.Tipo == 'EVCUSTODIAF') else listEvidenciasBool.append(b.IsValidada)
    Accept = False if(False in listEvidenciasBool) else True
    return Accept


def GetEvidenciaFisica(request):
    IDViaje = request.GET["XD_IDViaje"]
    Folio = request.GET["Folio"]
    EvidenciaFisica = list()
    TieneEvidenciasEnFalse = list()
    print(Folio)
    if "FTL" in Folio:
        GetEvidencias = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje = IDViaje, IsEvidenciaFisicaAprobada = 0)
        for ComprobarEvidenciaFisica in GetEvidencias:
            TieneEvidenciasEnFalse.append(ComprobarEvidenciaFisica.IsValidada)
        if False in TieneEvidenciasEnFalse:
            pass
        else:
            for EVFisica in GetEvidencias:
                newEvidenciasFisicas = {}
                newEvidenciasFisicas["XD_IDPedido"] =  EVFisica.IDBro_EvidenciaxViaje
                newEvidenciasFisicas["XD_IDViaje"] = EVFisica.IDBro_Viaje.IDBro_Viaje
                newEvidenciasFisicas["Delivery"] =  "BKG"
                EvidenciaFisica.append(newEvidenciasFisicas)
    else:
        for TieneEvidenciaValidada in XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga', 'Maniobras de carga'), Tipo="MESA CONTROL") | Q (IDXD_Viaje = IDViaje, Tipo = 'EVCUSTODIAF')).values('IsValidada'):
            if len(TieneEvidenciaValidada) >= 1:
                TieneEvidenciasEnFalse.append(TieneEvidenciaValidada['IsValidada'])
        for TieneEvidenciaDigital in XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje).values('IsEvidenciaPedidoxViaje'):
            if len(TieneEvidenciaDigital) >= 1:
                TieneEvidenciasEnFalse.append(TieneEvidenciaDigital['IsEvidenciaPedidoxViaje'])
        if False in TieneEvidenciasEnFalse:
            pass
        else:
            VerificarTipoEvidencia = XD_Viajes.objects.get(XD_IDViaje = IDViaje)
            for delibery in XD_EvidenciasxViaje.objects.filter(IDXD_Viaje = IDViaje, IsEvidenciaFisicaAprobada = 0) if(VerificarTipoEvidencia.TipoViaje == 'CUSTODIA') else XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje):
                if delibery.IsEnviada if(VerificarTipoEvidencia.TipoViaje == 'CUSTODIA') else not delibery.IsEvidenciaFisicaPedidoxViaje:
                    newEvidenciasFisicas = {}
                    newEvidenciasFisicas["XD_IDPedido"] = delibery.IDEvidenciaxViaje if(VerificarTipoEvidencia.TipoViaje == 'CUSTODIA') else delibery.XD_IDPedido.XD_IDPedido
                    newEvidenciasFisicas["XD_IDViaje"] = delibery.IDXD_Viaje if(VerificarTipoEvidencia.TipoViaje == 'CUSTODIA') else delibery.XD_IDViaje.XD_IDViaje
                    newEvidenciasFisicas["Delivery"] = delibery.Titulo if(VerificarTipoEvidencia.TipoViaje == 'CUSTODIA') else delibery.XD_IDPedido.Delivery
                    EvidenciaFisica.append(newEvidenciasFisicas)
    return JsonResponse({'EvidenciaFisica': EvidenciaFisica})


def SaveEvidenciaFisica(request):
    jParams = json.loads(request.body.decode('utf-8'))
    try:
        with transaction.atomic(using = 'XD_ViajesDB'):
            with transaction.atomic(using='bkg_viajesDB'):
                with transaction.atomic(using='users'):
                    if jParams["TipoEvidencia"] == "BKG":
                        SaveEvFisica = Bro_EvidenciasxViaje.objects.get(IDBro_EvidenciaxViaje = jParams['IDPedido'])
                        SaveEvFisica.IsEvidenciaFisicaAprobada = True
                        SaveEvFisica.IDUsuarioEvFisica = request.user.idusuario
                        SaveEvFisica.FechaEvFisica = datetime.datetime.now()
                        SaveEvFisica.save()
                        allEvFisicaTrue = EvidenciaFisicaCompletaBKG(SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                        if allEvFisicaTrue:
                            SaveEvFisicaViajes = Bro_Viajes.objects.get(IDBro_Viaje = SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                            SaveEvFisicaViajes.IsEvidenciasFisicas = True
                            SaveEvFisicaViajes.FechaRecEviFisicas = datetime.datetime.now()
                            SaveEvFisicaViajes.save()
                            GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.get(IDConcepto = SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                            SaveEvFisicaAdmon = PendientesEnviar.objects.get(IDPendienteEnviar = str(GetIDPendientesEnviar.IDPendienteEnviar))
                            SaveEvFisicaAdmon.IsEvidenciaFisica = True
                            SaveEvFisicaAdmon.save()
                            #request.get("http://api-admon-demo.logistikgo.com/api/Usuarios/SaveFolioHojaLiberacion", params = {"IDConcepto":SaveEvFisica.IDBro_Viaje.IDBro_Viaje, "Proyecto":"BKG"})
                    else:
                        SaveEvidenciaPedidosxViaje = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje = jParams['IDPedido']) if(jParams["TipoEvidencia"] == 'FOLIO' or jParams["TipoEvidencia"] == 'CORREO') else XD_PedidosxViajes.objects.get(XD_IDPedido = jParams['IDPedido'], XD_IDViaje = jParams['IDViaje'])
                        if jParams["TipoEvidencia"] == 'FOLIO' or jParams["TipoEvidencia"] == 'CORREO':
                            SaveEvidenciaPedidosxViaje.IsEvidenciaFisicaAprobada = True
                        else:
                            SaveEvidenciaPedidosxViaje.IsEvidenciaFisicaPedidoxViaje = True
                        SaveEvidenciaPedidosxViaje.IDUsuarioEvFisica = request.user.idusuario
                        SaveEvidenciaPedidosxViaje.FechaEvidenciaFisicaxPedidoxViaje = datetime.datetime.now()
                        SaveEvidenciaPedidosxViaje.save()
                        if jParams["TipoEvidencia"] != 'FOLIO' or jParams["TipoEvidencia"] != 'CORREO':
                            IsExpress = XD_Viajes.objects.get(XD_IDViaje = jParams['IDViaje'])
                            if IsExpress.TipoViaje == 'XPRESS':
                                GetIDPE = RelacionConceptoxProyecto.objects.filter(IDConcepto = jParams['IDPedido']).values("IDPendienteEnviar")
                                for Conceptos in GetIDPE:
                                    SaveEVFisPE = PendientesEnviar.objects.get(IDPendienteEnviar = Conceptos["IDPendienteEnviar"])
                                    if SaveEVFisPE.TipoConcepto == 'PEDIDO':
                                        SaveEVFisPE.IsEvidenciaFisica = True
                                        SaveEVFisPE.Status = "COMPLETO"
                                        SaveEVFisPE.save()
                        SaveXD_Viajes = ValidarEvidenciaXD_Viajea(jParams['IDViaje'])
                        if SaveXD_Viajes:
                            SaveBanderasXD_Viajes = XD_Viajes.objects.get(XD_IDViaje = jParams['IDViaje'])
                            SaveBanderasXD_Viajes.IsEvidenciaFisica = True
                            SaveBanderasXD_Viajes.FechaEvidenciaFisica = datetime.datetime.now()
                            # SaveBanderasXD_Viajes.Status = 'COMPLETO'
                            SaveBanderasXD_Viajes.save()
                            PedidoStatus = XD_PedidosxViajes.objects.filter(XD_IDViaje = jParams['IDViaje'])
                            if len(PedidoStatus) != 0:
                                for GetPedidoStatus in PedidoStatus:
                                    SavePedidoStatus = XD_PedidosxViajes.objects.get(XD_IDPedido = GetPedidoStatus.XD_IDPedido, XD_IDViaje = GetPedidoStatus.XD_IDViaje)
                                    SavePedidoStatus.StatusPedido = 'COMPLETO'
                                    SavePedidoStatus.save()
                            GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto = jParams['IDViaje']).values('IDPendienteEnviar')
                            for conceptos in GetIDPendientesEnviar:
                                SaveEvFisicaAdmon = PendientesEnviar.objects.get(IDPendienteEnviar = conceptos['IDPendienteEnviar'])
                                if SaveEvFisicaAdmon.TipoConcepto == 'VIAJE':
                                    SaveEvFisicaAdmon.IsEvidenciaFisica = True
                                    SaveEvFisicaAdmon.save()
                transaction.commit(using='users')
            transaction.commit(using='bkg_viajesDB')
        transaction.commit(using='XD_ViajesDB')
        print(jParams["TipoEvidencia"])
        api = descarga(jParams['IDViaje'], jParams["TipoEvidencia"])
        return HttpResponse(status=200)
    except Exception as e:
        transaction.rollback(using = 'XD_ViajesDB')
        transaction.rollback(using='bkg_viajesDB')
        transaction.rollback(using='users')
        print(e)
        return HttpResponse(status = 500)


def EvidenciaDigitalCompleta(request, viaje=""):
    IDViaje = request.GET["IDViaje"] if(viaje =="") else viaje
    TieneEvidenciaDigital = XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje)
    ListaTieneEvidenciaDigital = list()
    for TieneEvi in TieneEvidenciaDigital:
        ListaTieneEvidenciaDigital.append(TieneEvi.IsEvidenciaPedidoxViaje)
    TieneEvidenciaManiobrasAll = XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga', 'Maniobras de carga'), Tipo="MESA CONTROL") | Q(IDXD_Viaje = IDViaje, Tipo = 'EVCUSTODIAF'))
    for TieneEviManiobrasAll in TieneEvidenciaManiobrasAll:
        ListaTieneEvidenciaDigital.append(TieneEviManiobrasAll.IsValidada)
    IsEvidenciaDigitalCompleta = False if(False in ListaTieneEvidenciaDigital) else True
    if(viaje ==""):
        return JsonResponse({'IsEvidenciaDigitalCompleta': IsEvidenciaDigitalCompleta})
    else:
        return IsEvidenciaDigitalCompleta


def GetTituloForCustodia(Titulo):
    SplitTitulo = Titulo
    TituloSeparado = SplitTitulo.split("-")
    for GetTitulo in TituloSeparado:
        if "FOLIO" in GetTitulo:
            NewTitulo = GetTitulo
        elif "CORREO" in GetTitulo:
            NewTitulo = GetTitulo
    return NewTitulo


def FindFolioEvidenciaBGK(Folio, Transportista):
    try:
        GetIDViaje = Bro_Viajes.objects.get(Folio = Folio, StatusProceso = 'FINALIZADO', IDTransportista = Transportista)
        # ListaEvidencias=''
        if not Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje = GetIDViaje.IDBro_Viaje).exists():
            ListaEvidencias = readJson(GetIDViaje.Remisiones) if(len(GetIDViaje.Remisiones) >= 1) else readJson(0)
            for AddNewDataToJdon in ListaEvidencias:
                AddNewDataToJdon['XD_IDPedido'] = GetIDViaje.IDBro_Viaje
                AddNewDataToJdon['IDViaje'] =  GetIDViaje.IDBro_Viaje
                AddNewDataToJdon['TipoEvidencia'] = 'BKG'
                AddNewDataToJdon['RutaArchivo'] = ""
                AddNewDataToJdon['Status'] = 'Pendiente'
                AddNewDataToJdon['ComentarioRechazo'] = ""
        else:
            newlist = list()
            GetEvidencias = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje = GetIDViaje.IDBro_Viaje)
            for Evidencias in GetEvidencias:
                AddNewDataToJdon={}
                AddNewDataToJdon['XD_IDPedido'] = Evidencias.IDBro_EvidenciaxViaje
                AddNewDataToJdon['Delivery'] = Evidencias.Titulo
                AddNewDataToJdon['IDViaje'] =  Evidencias.IDBro_Viaje.IDBro_Viaje
                AddNewDataToJdon['TipoEvidencia'] = 'BKG'
                AddNewDataToJdon['RutaArchivo'] = Evidencias.RutaArchivo
                AddNewDataToJdon['Status'] = 'Enviada' if(Evidencias.IsEnviada and not Evidencias.IsRechazada and not Evidencias.IsValidada) else 'Rechazada' if(Evidencias.IsEnviada and Evidencias.IsRechazada) else 'Aprobada' if(Evidencias.IsEnviada and Evidencias.IsValidada) else 'Otro'
                AddNewDataToJdon['ComentarioRechazo'] = Evidencias.ComentarioRechazo
                newlist.append(AddNewDataToJdon)
            ListaEvidencias = newlist
        return {'ListaEvidencias': ListaEvidencias}
    except Exception as e:
        print(e)
        return {'Found' : False}


def readJson(Remisiones):
    # with open('static/json/EvidenciasxDefault.json') as file:
    #     data = json.load(file)
    GetDataEvidencias = JsonEvidenciasBKG()
    NewJson = list()
    for EvidenciaPrincipal in GetDataEvidencias['Principales']:
        AddDataToJson = {}
        AddDataToJson['Delivery'] = EvidenciaPrincipal['titulo']
        NewJson.append(AddDataToJson)
    if Remisiones != 0:
        TotalRemisiones = GetEachRemision(Remisiones)
        for addNewRemision in TotalRemisiones:
            NewRemision = {}
            NewRemision['Delivery'] = 'Remision'+'-'+addNewRemision
            NewJson.append(NewRemision)
    return NewJson

def GetEachRemision(Remision):
    TituloSeparado = Remision.split(",")
    NewRemision = list()
    for GetRemision in TituloSeparado:
        NewRemision.append(GetRemision.lstrip())
    return NewRemision

def EvidenciaDigitalCompletaBKG(request, IDViaje=""):
    IDViajeBKG = request.GET["IDViaje"] if(IDViaje=="") else IDViaje
    GetIDViaje = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje = IDViajeBKG)
    ListaEviBKG = list()
    for EachEvidence in GetIDViaje:
        ListaEviBKG.append(EachEvidence.IsValidada)
    AllValidadas = False if(False in ListaEviBKG) else True
    if IDViaje=="":
        return JsonResponse({"IsEvidenciaDigitalCompleta":AllValidadas})
    else:
        return AllValidadas

def EvidenciaFisicaCompletaBKG(IDViaje):
    GetEachEvFisica = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje = IDViaje)
    ListEVFisica = list()
    for EachEV in GetEachEvFisica:
        ListEVFisica.append(EachEV.IsEvidenciaFisicaAprobada)
    EvFisica = False if(False in ListEVFisica) else True
    return EvFisica

def IsViajeXpress(IDPedido,ViajeID):
    GetTipoViaje = XD_PedidosxViajes.objects.filter(XD_IDPedido = IDPedido)
    PedidosWithEvDig = list()
    ListaPedidosWithEvDig = list()
    for GetTipoTransporte in GetTipoViaje:
        if GetTipoTransporte.XD_IDViaje.TipoViaje == 'XPRESS':
            jsonTipo = {}
            jsonTipo['XD_IDPedido'] = GetTipoTransporte.XD_IDPedido.XD_IDPedido
            jsonTipo['XD_IDViaje'] = GetTipoTransporte.XD_IDViaje.XD_IDViaje
            jsonTipo['Tipo'] = GetTipoTransporte.TipoTransporte
            jsonTipo['TipoTransporte'] = GetTipoTransporte.XD_IDViaje.TipoViaje
            jsonTipo['IsEvidenciaDigital'] = GetTipoTransporte.IsEvidenciaPedidoxViaje
            PedidosWithEvDig.append(jsonTipo)
    print(PedidosWithEvDig)
    if len(PedidosWithEvDig) == 2:
        for i in PedidosWithEvDig:
            if i['XD_IDPedido'] == IDPedido and i['XD_IDViaje'] != ViajeID:
                ListaPedidosWithEvDig.append(i['IsEvidenciaDigital'])
        IsValido = False if( False in ListaPedidosWithEvDig) else True
    else:
        IsValido = False
    return IsValido

def VerificarSaveViajePE(IDPedido):
    GetIDViajes = XD_PedidosxViajes.objects.filter(XD_IDPedido = IDPedido)
    IDViajes = list()
    for Each in GetIDViajes:
        IDViajes.append(Each.XD_IDViaje.XD_IDViaje)
    return IDViajes

def GetAllEvidecesDigitalsT1yT2(IDViaje):
    GetPedidos = XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje)
    ListaPedidos = list()
    for i in GetPedidos:
        # a = XD_PedidosxViajes.objects.filter(XD_IDPedido = i.XD_IDPedido)
        # for j in a:
        ListaPedidos.append(i.IsEvidenciaPedidoxViaje)
    TrueORFALSE = False if False in ListaPedidos else True
    print(TrueORFALSE)
    return TrueORFALSE


def DescargarHojaLiberacion(request):
    IDViaje = request.GET["IDViaje"]
    Proyecto = request.GET["Proyecto"]
    if Proyecto == 'BKG':
        GetRutaHojaLiberacion = Bro_Viajes.objects.get(IDBro_Viaje = IDViaje, IsEvidenciasDigitales = 1, IsEvidenciasFisicas = 1)
        if not GetRutaHojaLiberacion.IsDescargaHojaLiberacion or GetRutaHojaLiberacion.IsDescargaHojaLiberacion is None:
            HojaLiberacion = GetRutaHojaLiberacion.RutaHojaLiberacion
            if HojaLiberacion is not None:
                GetRutaHojaLiberacion.IsDescargaHojaLiberacion = True
                GetRutaHojaLiberacion.save()
        else:
            HojaLiberacion = False
    else:
        GetRutaHojaLiberacion = XD_Viajes.objects.get(XD_IDViaje=IDViaje, IsEvidenciaPedidos=1, IsEvidenciaFisica=1)
        if not GetRutaHojaLiberacion.IsDescargaHojaLiberacion or GetRutaHojaLiberacion.IsDescargaHojaLiberacion is None:
            HojaLiberacion = GetRutaHojaLiberacion.RutaHojaEmbarqueCosto
            if HojaLiberacion is not None:
                GetRutaHojaLiberacion.IsDescargaHojaLiberacion = True
                GetRutaHojaLiberacion.save()
        else:
            HojaLiberacion = False
        # HojaLiberacion = GetRutaHojaLiberacion.RutaHojaEmbarqueCosto
    return JsonResponse({'HojaLiberacion':HojaLiberacion})


def JsonEvidenciasBKG():
    JsonData = {
        "Principales":
        [
        {
          "titulo": "CUSTOMS ENTRY",
          "tipo": "EVIDENCIA"
        },
        {
          "titulo": "FISCAL STAMP",
          "tipo": "EVIDENCIA"
        },
        {
          "titulo": "LEFT SIDE",
          "tipo": "EVIDENCIA"
        },
        {
          "titulo": "RIGHT SIDE",
          "tipo": "EVIDENCIA"
        },
        {
          "titulo": "REMISSION",
          "tipo": "EVIDENCIA"
        },
        {
          "titulo": "LOAD EVIDENCE",
          "tipo": "EVIDENCIA"
        },
        {
          "titulo": "BILL OF LADING",
          "tipo": "EVIDENCIA"
        },
        {
          "titulo": "REAR SIDE",
          "tipo": "EVIDENCIA"
        }
        ]
    }
    return JsonData

def FilterBy(request):
    Proveedores = json.loads(request.GET["Proveedor"])
    Proyectos = json.loads(request.GET["Proyecto"])
    if "Year" in request.GET:
        arrMonth = json.loads(request.GET["arrMonth"])
        Year = request.GET["Year"]
        if ("BKG" in Proyectos and "XD" in Proyectos) or Proyectos == []:
            Evidencias = Bro_Viajes.objects.filter(FechaDescarga__month__in = arrMonth, FechaDescarga__year = Year)
            Evidencias = XD_Viajes.objects.filter(FechaDespacho__month__in = arrMonth, FechaDespacho__year = Year)
        elif "BKG" in Proyectos and "XD" not in Proyectos:
            Evidencias = Bro_Viajes.objects.filter(FechaDescarga__month__in = arrMonth, FechaDescarga__year = Year)
        elif "XD" in Proyectos and "BKG" not in Proyectos:
            Evidencias = XD_Viajes.objects.filter(FechaDespacho__month__in = arrMonth, FechaDespacho__year = Year)
    else:
        if "BKG" in Proyectos and "XD" in Proyectos:
            Evidencias = Bro_Viajes.objects.filter(FechaDescarga__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')])
            Evidencias = XD_Viajes.objects.filter(FechaDespacho__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')])
        elif "BKG" in Proyectos and "XD" not in Proyectos:
            Evidencias = Bro_Viajes.objects.filter(FechaDescarga__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')])
        elif "XD" in Proyectos and "BKG" not in Proyectos:
            Evidencias = XD_Viajes.objects.filter(FechaDespacho__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')])
        # Evidencias = Bro_Viajes.objects.filter(FechaDescarga__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')]).exclude(StatusFacturaProveedor = 'DEPURADO')
    if Proveedores:
        if ("BKG" in Proveedores and "XD" in Proveedores) or Proveedores == []:
            Evidencias = Bro_Viajes.objects.filter(IDTransportista__in = Proveedores)
            Evidencias = XD_Viajes.objects.filter(IDTransportista__in = Proveedores)
        elif "BKG" in Proveedores and "XD" not in Proveedores:
            Evidencias = Bro_Viajes.objects.filter(IDTransportista__in = Proveedores)
        elif "XD" in Proveedores and "BKG" not in Proveedores:
            Evidencias = XD_Viajes.objects.filter(IDTransportista__in = Proveedores)
    # ListData = PEToList(Evidencias)
    htmlRes = render_to_string('TablaEvidenciasMesaControl.html', {'EvidenciasxAprobar':Evidencias}, request = request,)
    return JsonResponse({'htmlRes' : htmlRes})

def uploadEvidencias(request):
    if request.POST['type'] == 'application/pdf':
        namefile = str(uuid.uuid4()) + ".pdf"
    elif request.POST['type'] == 'image/jpeg':
        namefile = str(uuid.uuid4()) + ".jpg"
    elif request.POST['type'] == 'image/png':
        namefile = str(uuid.uuid4()) + ".png"
    container_client = "evidencias"
    blob_service_client = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=http;AccountName=lgklataforma;AccountKey=SpHagQjk7C4dBPv1cse9w36zmAtweXIMjcw9DWve7ipgXgf2Fa5l+vw2k57EM8uinlUOkfxt34BQpC9FBHE+Yg==",container_name=container_client, blob_name=namefile)
    blob_service_client.upload_blob(request.FILES['files[]'])
    urlFile = blob_service_client.url
    print(urlFile)
    return JsonResponse({"url":urlFile})


def descarga(IDViaje, Proyecto):
    sendAPI = CheckAllEvidenciaFisicaPedidoTrue(IDViaje) if Proyecto != "BKG" else CheckAllEvidenciaFisicaTrue(IDViaje)
    if sendAPI:
        Project = "BKG" if Proyecto == "BKG" else "XD"
        jsonParams = {'IDConcepto': IDViaje, 'Proyecto':Project}
        respose = requests.post("http://api-admon-demo.logistikgo.com/api/Usuarios/SaveFolioHojaLiberacion",
                                headers={'content-type': 'application/json'}, json=jsonParams)
        return respose.status_code
    else:
        return "ok"

def CheckAllEvidenciaFisicaPedidoTrue(IDViaje):
    GetEvidenciasFisicas = XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje)
    if len(GetEvidenciasFisicas) == 0:
        GetEvidenciasFisicasCustodia = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje,
                                                                          Titulo__in=("FOLIO", "CORREO"))
        Listevidencias = list()
        for EachPedido in GetEvidenciasFisicasCustodia:
            itHasEvidencias = True if EachPedido.IsEvidenciaFisicaAprobada else False
            Listevidencias.append(itHasEvidencias)
        AllEvidencesInTrue = True if len(Listevidencias) == 2 and False not in Listevidencias else False
        return AllEvidencesInTrue
    else:
        Listevidencias = list()
        for EachPedido in GetEvidenciasFisicas:
            itHasEvidencias = True if EachPedido.IsEvidenciaFisicaPedidoxViaje else False
            Listevidencias.append(itHasEvidencias)
        AllEvidencesInTrue = True if False not in Listevidencias else False
        return AllEvidencesInTrue
    # else:
    #     GetEvidenciasFisicasCustodia = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Titulo__in=("FOLIO", "CORREO"))
    #     Listevidencias = list()
    #     for EachPedido in GetEvidenciasFisicasCustodia:
    #         itHasEvidencias = True if EachPedido.IsEvidenciaFisicaAprobada else False
    #         Listevidencias.append(itHasEvidencias)
    #     print(len(Listevidencias))
    #     print(Listevidencias)
    #     AllEvidencesInTrue = True if len(Listevidencias) == 2 and False not in Listevidencias else False
    #     return AllEvidencesInTrue

def CheckAllEvidenciaFisicaTrue(IDViaje):
    GetEvidenciasFisicas = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje = IDViaje)
    Listevidencias = list()
    for EachEvidencia in GetEvidenciasFisicas:
        itHasEvidencias = True if EachEvidencia.IsEvidenciaFisicaAprobada else False
        Listevidencias.append(itHasEvidencias)
    AllEvidencesInTrue = True if False not in Listevidencias else False
    return AllEvidencesInTrue

def fechaevidencias(request):
    viajes = XD_Viajes.objects.filter(Status = 'FINALIZADO', IsEvidenciaFisica = 1, FechaDespacho__gte = '2020-07-01', FechaEvidenciaFisica = None)
    for eachviaje in viajes:
        fechapedido = XD_PedidosxViajes.objects.filter(XD_IDViaje = eachviaje.XD_IDViaje).last()
        fechapedidoEv = XD_EvidenciasxPedido.objects.filter(XD_IDViaje=eachviaje.XD_IDViaje).last()
        if eachviaje.TipoViaje != "CUSTODIA":
            saveFecha = XD_Viajes.objects.get(XD_IDViaje = eachviaje.XD_IDViaje)
            if fechapedidoEv.FechaValidacion is not None:
                saveFecha.FechaEvidenciaFisica = fechapedidoEv.FechaValidacion + datetime.timedelta(days=2) if fechapedido.FechaEvidenciaFisicaxPedidoxViaje is None else fechapedido.FechaEvidenciaFisicaxPedidoxViaje
            else:
                saveFecha.FechaEvidenciaFisica = fechapedidoEv.FechaCaptura + datetime.timedelta(
                    days=2) if fechapedido.FechaEvidenciaFisicaxPedidoxViaje is None else fechapedido.FechaEvidenciaFisicaxPedidoxViaje
            saveFecha.save()
            if fechapedido.FechaEvidenciaFisicaxPedidoxViaje is None:
                fepedido = XD_PedidosxViajes.objects.filter(XD_IDViaje = eachviaje.XD_IDViaje)
                for i in fepedido:
                    savepediodfe = XD_PedidosxViajes.objects.get(XD_PedidoxViaje = i.XD_PedidoxViaje)
                    if fechapedidoEv.FechaValidacion is not None:
                        savepediodfe.FechaEvidenciaFisicaxPedidoxViaje = fechapedidoEv.FechaValidacion + datetime.timedelta(
                         days=2)
                    else:
                        savepediodfe.FechaEvidenciaFisicaxPedidoxViaje = fechapedidoEv.FechaCaptura + datetime.timedelta(
                            days=2)
                    savepediodfe.save()
        else:
            fechacustodia = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=eachviaje.XD_IDViaje, Tipo='EVCUSTODIAF').last()
            saveFecha = XD_Viajes.objects.get(XD_IDViaje=eachviaje.XD_IDViaje)
            if fechacustodia.FechaValidacion is not None:
                saveFecha.FechaEvidenciaFisica =fechacustodia.FechaValidacion + datetime.timedelta(
                    days=2) if fechacustodia.FechaEvidenciaFisicaxPedidoxViaje is None else fechacustodia.FechaEvidenciaFisicaxPedidoxViaje
            else:
                saveFecha.FechaEvidenciaFisica = fechacustodia.FechaCaptura + datetime.timedelta(
                    days=2) if fechacustodia.FechaEvidenciaFisicaxPedidoxViaje is None else fechacustodia.FechaEvidenciaFisicaxPedidoxViaje
            saveFecha.save()
            if fechacustodia.FechaEvidenciaFisicaxPedidoxViaje is None:
                eachEv = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=eachviaje.XD_IDViaje, Tipo='EVCUSTODIAF')
                for i in eachEv:
                    saveEv = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje=i.IDEvidenciaxViaje)
                    if fechacustodia.FechaValidacion is not None:
                        saveEv.FechaEvidenciaFisicaxPedidoxViaje = fechacustodia.FechaValidacion + datetime.timedelta(days=2)
                    else:
                        saveEv.FechaEvidenciaFisicaxPedidoxViaje = fechacustodia.FechaCaptura + datetime.timedelta(
                            days=2)
                    saveEv.save()


def fechaevdigital(request):
    viajes = XD_Viajes.objects.filter(Status='FINALIZADO', IsEvidenciaPedidos=1, FechaDespacho__gte='2020-07-01',
                                      FechaEvidenciaDigital=None)
    for i in viajes:
        if i.TipoViaje != "CUSTODIA":
            fecha = XD_EvidenciasxPedido.objects.filter(XD_IDViaje = i.XD_IDViaje).last()
            savev = XD_Viajes.objects.get(XD_IDViaje = i.XD_IDViaje)
            savev.FechaEvidenciaDigital = fecha.FechaValidacion
            savev.save()

def GetEvidenciasCXP(request):
    IDViaje = request.GET["XD_IDViaje"]
    Folio = request.GET["Folio"]
    ListEvidencias = list()
    try:
        if "FTL" in Folio:
            getEvidencias = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje = IDViaje)
            for evidencias in getEvidencias:
                jsonevidencias = {}
                jsonevidencias["Titulo"] = evidencias.Titulo
                jsonevidencias["RutaArchivo"] = evidencias.RutaArchivo
                ListEvidencias.append(jsonevidencias)
            return JsonResponse({"Evidencias": ListEvidencias})
        else:
            getEvidenciaxPedido = XD_EvidenciasxPedido.objects.filter(XD_IDViaje = IDViaje)
            for evidencias in getEvidenciaxPedido:
                jsonevidencias = {}
                TituloPedido = XD_PedidosxViajes.objects.get(XD_IDPedido = evidencias.IDXD_Pedido, XD_IDViaje = evidencias.XD_IDViaje)
                jsonevidencias["Titulo"] = TituloPedido.XD_IDPedido.Delivery
                jsonevidencias["RutaArchivo"] = evidencias.RutaArchivo
                ListEvidencias.append(jsonevidencias)
            getEvidenciaxCustodia= XD_EvidenciasxViaje.objects.filter(IDXD_Viaje = IDViaje, Tipo="EVCUSTODIAF", Titulo__in=('CORREO', 'FOLIO'))
            for evidenciasCustodias in getEvidenciaxCustodia:
                jsonevidencias = {}
                jsonevidencias["Titulo"] = evidenciasCustodias.Titulo
                jsonevidencias["RutaArchivo"] = evidenciasCustodias.RutaArchivo
                ListEvidencias.append(jsonevidencias)
            gerEvidenciasxManiobras = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Tipo__in=("MESA CONTROL","EVIDENCIA ACCESORIOS"), Titulo__in=('Maniobras de carga', 'Maniobras de descarga'))
            for EvidenciasManiobras in gerEvidenciasxManiobras:
                jsonevidencias = {}
                jsonevidencias["Titulo"] = EvidenciasManiobras.Titulo
                jsonevidencias["RutaArchivo"] = EvidenciasManiobras.RutaArchivo
                ListEvidencias.append(jsonevidencias)
            return JsonResponse({"Evidencias": ListEvidencias})
    except Exception as e:
        print(e)
        return HttpResponse(status=500)



def CreateCartaNoadeudoMC(request):
    try:
        w, h = A4
        date = datetime.datetime.now()
        months = (
            "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
            "Noviembre",
            "Diciembre")
        day = date.day
        NombreProveedor = Proveedor.objects.get(IDTransportista=455)
        month = months[date.month - 1]
        year = date.year
        messsage = "{} de {} del {}".format(day, month, year)
        bufferMemoria = BytesIO()
        c = canvas.Canvas(bufferMemoria, pagesize=A4)
        c.setTitle("CartaNoAdeudo.pdf")
        p = ParagraphStyle('test')
        p.alignment = TA_JUSTIFY
        p.fontSize = 13
        p.leading = 20
        p1 = ParagraphStyle('test')
        p1.alignment = TA_CENTER
        p1.fontSize = 13
        p1.leading = 15
        c.drawImage('static/img/F.png', -1, 5, 600, 841)
        c.drawString(300, 690, "San Luis Potosí, S.L.P. a " + str(messsage))
        c.drawString(100, 640, "Logisti-k de México SA de CV")
        c.drawString(100, 620, "Av. Chapultepec #1385 3er. Piso")
        c.drawString(100, 600, "Privadas del Pedregal, S.L.P.")
        c.drawString(100, 550, "ATENCION:")
        c.drawString(100, 520, "C.P. Judith Castillo Zavala")
        c.drawString(100, 500, "Gerente de Finanzas")
        c.drawString(100, 450, "Asunto: Carta de no adeudo de hoja de liberación")
        para = Paragraph(
            "Por medio de la presente me dirijo a usted para informar que no existen viajes pendientes de Hoja de Liberación "
            "por parte de Logisti-k a " + NombreProveedor.RazonSocial + " al 20 de " + months[
                date.month - 2] + " del " + str(year) + ".", p)
        para.wrapOn(c, 420, 600)
        para.drawOn(c, 100, 350)
        c.drawString(100, 300, "Sin más por el momento reciba un cordial saludo.")
        c.drawString(250, 200, "ATENTAMENTE:")
        c.line(200, 142, 390, 142)
        c.drawString(250, 130, "(Nombre y firma)")
        NomProv = Paragraph(NombreProveedor.RazonSocial, p1)
        NomProv.wrapOn(c, 200, 40)
        NomProv.drawOn(c, 200, 90)
        c.showPage()
        c.save()
        pdf = bufferMemoria.getvalue()
        bufferMemoria.close()
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="CartaNoAdeudo.pdf"'
        response.write(pdf)
        return response
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

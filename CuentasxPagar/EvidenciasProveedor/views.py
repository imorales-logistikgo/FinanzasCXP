import urllib
import uuid
import io

from django.conf import settings
from azure.storage.blob import BlobClient
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from XD_Viajes.models import XD_Viajes, XD_PedidosxViajes, XD_Pedidos, XD_AccesoriosxViajes, XD_EvidenciasxPedido, XD_EvidenciasxViaje, Ext_Viajes_MesaControl as Ext_Viajes_MesaControlXD
from PendientesEnviar.models import PendientesEnviar, RelacionConceptoxProyecto
from usersadmon.models import AdmonUsuarios,Proveedor, View_EvidenciasCxP
from bkg_viajes.models import Bro_Viajes, Bro_EvidenciasxViaje, Ext_Viajes_MesaControl
import json, datetime
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json
from itertools import chain
import requests
from django.template.loader import render_to_string
from PendientesEnviar import views

@login_required
def EvidenciasProveedor(request):
    if request.user.roles == 'MesaControl' or request.user.is_superuser:
        EvidenciasxAprobar = XD_Viajes.objects.filter(Status = 'FINALIZADO', FechaDespacho__month = datetime.datetime.now().month, FechaDespacho__year = datetime.datetime.now().year).exclude(Status = 'CANCELADO')
        EvidenciasxAprobarBKG = Bro_Viajes.objects.filter(StatusProceso = 'FINALIZADO', FechaDescarga__month = datetime.datetime.now().month, FechaDescarga__year = datetime.datetime.now().year).exclude(StatusProceso = 'CANCELADO')
        Evidencias = chain(EvidenciasxAprobar, EvidenciasxAprobarBKG)
        SinEvidenciaDigitalXD = XD_Viajes.objects.filter(IsEvidenciaPedidos = False).count()
        SinEvidenciaDigitalBKG = Bro_Viajes.objects.filter(IsEvidenciasDigitales = False).count()
        SinEvidenciaDigital = SinEvidenciaDigitalXD+SinEvidenciaDigitalBKG
        Proveedores = Proveedor.objects.all()
        EvidenciasByWendo = View_EvidenciasCxP.objects.all()
        return render(request, 'EvidenciasProveedor.html', {'Evidencias': EvidenciasByWendo,'EvidenciasxAprobar': Evidencias, 'EvidenciaDigital': SinEvidenciaDigital, 'Proveedores':Proveedores})
    elif request.user.roles == 'Proveedor':
        # SinEvidenciaDigital = XD_Viajes.objects.filter(IsEvidencia = False).count()
        # SinEvidenciaFisica = XD_Viajes.objects.filter(IsEvidenciaFisica = False).count()
        return render(request, 'EvidenciasProveedor.html')
    elif request.user.roles == 'users':
        return HttpResponse(status=403)
    elif request.user.roles == 'CXP' or request.user.is_superuser:
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
            XDFolio = XD_Viajes.objects.exclude(Status='CANCELADO').get(Folio=Folio, Status='FINALIZADO', IDTransportista=request.user.IDTransportista)
            if XDFolio.TipoViaje == 'CUSTODIA':
                GetEvidenciaxManiobra = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=XDFolio.XD_IDViaje, Tipo='EVCUSTODIAF', Titulo="FOLIO")
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
                    # for i in range(2):
                    newDelivery = {}
                    newDelivery['XD_IDPedido'] = XDFolio.XD_IDViaje
                    newDelivery['Delivery'] = XDFolio.Folio + "-" + "FOLIO"
                    newDelivery['IDViaje'] = XDFolio.XD_IDViaje
                    newDelivery['TipoEvidencia'] = 'Custodia'
                    newDelivery['RutaArchivo'] = ''
                    newDelivery['Status'] = 'Pendiente'
                    newDelivery['ComentarioRechazo'] = ""
                    arrFoliosEvidencias.append(newDelivery)
            else:
                GetDelivery = XD_PedidosxViajes.objects.filter(XD_IDViaje=XDFolio.XD_IDViaje)#, StatusPedido = 'ENTREGADO')
                if GetDelivery:
                    EvidenciaByObservacion = GetObservacionesByPedidos(XDFolio.XD_IDViaje)
                    if len(EvidenciaByObservacion) >= 1:
                        for eachpedido in EvidenciaByObservacion:
                            if not XD_EvidenciasxPedido.objects.filter(XD_IDViaje=eachpedido["IDViaje"], IDXD_Pedido=eachpedido["XD_IDPedido"], Titulo='BITACORA').exists():
                                arrFoliosEvidencias.append(eachpedido)
                            else:
                                newDelivery = {}
                                newDelivery['XD_IDPedido'] = eachpedido["XD_IDPedido"]
                                newDelivery['Delivery'] = eachpedido["Delivery"]
                                newDelivery['IDViaje'] = eachpedido["IDViaje"]
                                newDelivery['TipoEvidencia'] = eachpedido["TipoEvidencia"]
                                newDelivery['RutaArchivo'] = ""
                                newDelivery['Status'] = "Enviada" if XD_EvidenciasxPedido.objects.filter(XD_IDViaje=eachpedido["IDViaje"], IDXD_Pedido=eachpedido["XD_IDPedido"], Titulo='BITACORA', IsValidada=0, IsRechazada=0, IsEnviada=1).exists() else "Aprobada" if XD_EvidenciasxPedido.objects.filter(XD_IDViaje=eachpedido["IDViaje"], IDXD_Pedido=eachpedido["XD_IDPedido"], Titulo='BITACORA', IsValidada=1, IsRechazada=0, IsEnviada=1).exists() else "Rechazada" if XD_EvidenciasxPedido.objects.filter(XD_IDViaje=eachpedido["IDViaje"], IDXD_Pedido=eachpedido["XD_IDPedido"], Titulo='BITACORA', IsValidada=0, IsRechazada=1, IsEnviada=1).exists() else "Otro"
                                newDelivery['ComentarioRechazo'] = ""
                                arrFoliosEvidencias.append(newDelivery)
                    for Delivery in GetDelivery:
                        if len(XD_EvidenciasxPedido.objects.filter(IDXD_Pedido=Delivery.XD_IDPedido.XD_IDPedido, XD_IDViaje=Delivery.XD_IDViaje.XD_IDViaje, Titulo='EVIDENCIA1')) >= 1:
                            TieneEvidencia = XD_EvidenciasxPedido.objects.filter(IDXD_Pedido=Delivery.XD_IDPedido.XD_IDPedido, XD_IDViaje=Delivery.XD_IDViaje.XD_IDViaje, Titulo='EVIDENCIA1')
                            for TieneEvidencia1 in TieneEvidencia:
                                newDelivery = {}
                                newDelivery['XD_IDPedido'] = Delivery.XD_IDPedido.XD_IDPedido
                                newDelivery['Delivery'] = Delivery.XD_IDPedido.Delivery.replace(".","") if TieneEvidencia1.Titulo != 'BITACORA' else GetObservacionesByPedidoT1(Delivery.XD_IDPedido.Observaciones, Delivery.TipoTransporte)
                                newDelivery['IDViaje'] = Delivery.XD_IDViaje.XD_IDViaje
                                newDelivery['TipoEvidencia'] = 'Pedido' if TieneEvidencia1.Titulo != 'BITACORA' else 'Bitacora'
                                newDelivery['RutaArchivo'] = '' if(TieneEvidencia1.IsEnviada and TieneEvidencia1.IsRechazada) else TieneEvidencia1.RutaArchivo
                                newDelivery['Status'] = 'Rechazada' if(TieneEvidencia1.IsEnviada and TieneEvidencia1.IsRechazada) else 'Aprobada' if(TieneEvidencia1.IsValidada) else  "Enviada" if (TieneEvidencia1.IsEnviada and not TieneEvidencia1.IsRechazada and not TieneEvidencia1.IsValidada) else "Otro"
                                newDelivery['ComentarioRechazo'] = TieneEvidencia1.ComentarioRechazo
                                arrFoliosEvidencias.append(newDelivery)
                        else:
                            newDelivery = {}
                            newDelivery['XD_IDPedido'] = Delivery.XD_IDPedido.XD_IDPedido
                            newDelivery['Delivery'] = Delivery.XD_IDPedido.Delivery.replace(".","")
                            newDelivery['IDViaje'] = Delivery.XD_IDViaje.XD_IDViaje
                            newDelivery['TipoEvidencia'] = 'Pedido'
                            newDelivery['RutaArchivo'] = "" #if (Delivery.IsEvidenciaPedidoxViaje or Delivery.IsEvidenciaFisicaPedidoxViaje) else ""
                            newDelivery['Status'] = 'Otro' if (
                                        Delivery.IsEvidenciaPedidoxViaje or Delivery.IsEvidenciaFisicaPedidoxViaje) else 'Pendiente'
                            # newDelivery['RutaArchivo'] = "" if(GetDelivery[0].IsEvidenciaPedidoxViaje == 1 or GetDelivery[0].IsEvidenciaFisicaPedidoxViaje == 1) else ""
                            # newDelivery['Status'] = 'Otro' if(GetDelivery[0].IsEvidenciaPedidoxViaje == 1 or GetDelivery[0].IsEvidenciaFisicaPedidoxViaje == 1) else 'Pendiente'
                            newDelivery['ComentarioRechazo'] = ""
                            arrFoliosEvidencias.append(newDelivery)
            for Maniobras in XD_AccesoriosxViajes.objects.filter(XD_IDViaje=XDFolio.XD_IDViaje, Descripcion__in=('Maniobras de descarga', 'Maniobras de carga')):
                if Maniobras:
                    GetManiobras = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=Maniobras.XD_IDViaje, Titulo__in=('Maniobras de descarga', 'Maniobras de carga'), Tipo="MESA CONTROL")
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
                        SaveEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDXD_Pedido=Evidencias['IDPedido'], XD_IDViaje=Evidencias['IDViaje'], Titulo='EVIDENCIA1') if(Evidencias['TipoEvidencia'] == 'Pedido') else XD_EvidenciasxPedido.objects.get(IDXD_Pedido=Evidencias['IDPedido'], XD_IDViaje=Evidencias['IDViaje'], Titulo=Evidencias['TipoEvidencia'].upper()) if(Evidencias['TipoEvidencia'] == 'Bitacora') else XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje =Evidencias['IDPedido'], IDXD_Viaje = Evidencias['IDViaje']) if(Evidencias['TipoEvidencia'] == 'Maniobras' or Evidencias['TipoEvidencia'] == 'Custodia') else ""
                        SaveEvidenciaxPedido.FechaCaptura = datetime.datetime.now()
                        SaveEvidenciaxPedido.NombreArchivo = Evidencias['NombreArchivo']
                        SaveEvidenciaxPedido.RutaArchivo = Evidencias['Evidencia']
                        SaveEvidenciaxPedido.IsRechazada = False
                        SaveEvidenciaxPedido.IsEnviada = True
                        SaveEvidenciaxPedido.IsRemplazada = True
                        SaveEvidenciaxPedido.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario=request.user.idusuario)
                        SaveEvidenciaxPedido.save()
                    # return HttpResponse(status = 200)
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
                        SaveEvidenciaxPedido = XD_EvidenciasxPedido() if(Evidencias['TipoEvidencia'] == 'Pedido' or Evidencias['TipoEvidencia'] == 'Bitacora') else XD_EvidenciasxViaje() if(Evidencias['TipoEvidencia'] == 'Maniobras' or Evidencias['TipoEvidencia'] == 'Custodia') else ""
                        SaveEvidenciaxPedido.IDXD_Pedido = Evidencias['IDPedido'] if(Evidencias['TipoEvidencia'] == 'Pedido' or Evidencias['TipoEvidencia'] == 'Bitacora') else None
                        if Evidencias['TipoEvidencia'] == 'Pedido' or Evidencias['TipoEvidencia'] == 'Bitacora':
                            SaveEvidenciaxPedido.XD_IDViaje = Evidencias['IDViaje']
                        elif Evidencias['TipoEvidencia'] == 'Maniobras' or Evidencias['TipoEvidencia'] == 'Custodia':
                            SaveEvidenciaxPedido.IDXD_Viaje = Evidencias['IDViaje']
                        SaveEvidenciaxPedido.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario=request.user.idusuario)
                        SaveEvidenciaxPedido.FechaCaptura = datetime.datetime.now()
                        SaveEvidenciaxPedido.Titulo = 'EVIDENCIA1' if(Evidencias['TipoEvidencia'] == 'Pedido') else TituloEvidencia if(Evidencias['TipoEvidencia'] == 'Maniobras') else TituloCustodia if(Evidencias['TipoEvidencia'] == 'Custodia') else "BITACORA" if Evidencias['TipoEvidencia'] == 'Bitacora' else ""
                        SaveEvidenciaxPedido.Tipo = 'EVIDENCIA' if(Evidencias['TipoEvidencia'] == 'Pedido' or Evidencias['TipoEvidencia'] == 'Bitacora') else 'MESA CONTROL' if(Evidencias['TipoEvidencia'] == 'Maniobras') else "EVCUSTODIAF" if(Evidencias['TipoEvidencia'] == 'Custodia') else ""
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
        return HttpResponse(status=200)
    except Exception as e:
            print(e)
            transaction.rollback(using='XD_ViajesDB')
            return HttpResponse(status=500)



def GetEvidenciasMesaControl(request):
    IDViaje = request.GET["XD_IDViaje"]
    Folio = request.GET["Folio"]
    ListEvidencias = list()
    try:
        if "FTL" in Folio:
            GetEvidenciasValidarBGK = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje=IDViaje, IsEnviada=1, IsRechazada=0, IsValidada=0)
            for EvidenciaBKG in GetEvidenciasValidarBGK:
                AddEvidencia = {}
                AddEvidencia['IDEvidencia'] = EvidenciaBKG.IDBro_EvidenciaxViaje
                AddEvidencia['URLEvidencia'] = EvidenciaBKG.RutaArchivo
                AddEvidencia['Delivery'] = EvidenciaBKG.Titulo
                AddEvidencia['TipoEvidencia'] = 'BKG'
                AddEvidencia['IDViaje'] = EvidenciaBKG.IDBro_Viaje.IDBro_Viaje
                ListEvidencias.append(AddEvidencia)
        else:
            GetIDPedidos = XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje)
            if not ValidacionEviByObservaciones(IDViaje) and GetIDPedidos[0].XD_IDViaje.IDClienteFiscal == 5267:
                return HttpResponse(status=500)
            TotalObservaciones = CountTotalEvidencias(GetIDPedidos)
            TotalEvidencias = XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje).count() + TotalObservaciones
            if XD_EvidenciasxPedido.objects.filter(XD_IDViaje=IDViaje).count() == TotalEvidencias:
                for GetPedidos in GetIDPedidos:
                    GetDelivery = XD_Pedidos.objects.get(XD_IDPedido=GetPedidos.XD_IDPedido.XD_IDPedido)
                    GetEvidenciaxPedido = XD_EvidenciasxPedido.objects.filter(IDXD_Pedido=GetPedidos.XD_IDPedido.XD_IDPedido, XD_IDViaje=IDViaje)
                    for eachEvidenciaxPedido in GetEvidenciaxPedido:
                        if eachEvidenciaxPedido.IsEnviada and not eachEvidenciaxPedido.IsValidada and not eachEvidenciaxPedido.IsRechazada:
                            AddEvidencia = {}
                            AddEvidencia['IDEvidencia'] = eachEvidenciaxPedido.IDEvidenciaxPedido
                            AddEvidencia['URLEvidencia'] = eachEvidenciaxPedido.RutaArchivo
                            AddEvidencia['Delivery'] = GetDelivery.Delivery.replace('.',"") if eachEvidenciaxPedido.Titulo != "BITACORA" else GetObservacionesByPedidoT1(GetDelivery.Observaciones, GetPedidos.TipoTransporte)
                            AddEvidencia['TipoEvidencia'] = 'Pedido' if eachEvidenciaxPedido.Titulo != "BITACORA" else 'Bitacora'
                            AddEvidencia['IDViaje'] = eachEvidenciaxPedido.XD_IDViaje
                            ListEvidencias.append(AddEvidencia)
            else:
                return HttpResponse(status=500)
            GetEvidenciasxViaje = XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje=IDViaje, Titulo__in=('Maniobras de descarga','Maniobras de carga'), Tipo='MESA CONTROL') | Q(IDXD_Viaje=IDViaje, Tipo='EVCUSTODIAF'))
            # ListEvi = EvidenciasToList(GetEvidenciasxViaje)
            for Maniobras in GetEvidenciasxViaje: #ListEvi:
                if Maniobras.Titulo and not Maniobras.IsValidada and not Maniobras.IsRechazada:
                    if Maniobras.Tipo == 'EVCUSTODIAF' and len(GetEvidenciasxViaje) < 2:
                        pass
                    else:
                        AddManiobras = {}
                        AddManiobras["IDEvidencia"] = Maniobras.IDEvidenciaxViaje
                        AddManiobras['URLEvidencia'] = Maniobras.RutaArchivo
                        AddManiobras['Delivery'] = Maniobras.Titulo
                        AddManiobras['TipoEvidencia'] = "Custodia" if(Maniobras.Tipo == 'EVCUSTODIAF') else "Maniobras"
                        AddManiobras['IDViaje'] = Maniobras.IDXD_Viaje
                        ListEvidencias.append(AddManiobras)
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
                    if jParams['TipoEvidencia'] == 'Pedido' or jParams['TipoEvidencia'] == 'Bitacora':
                        SaveEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDEvidenciaxPedido=jParams['IDSaveEvidencia'])
                        SaveEvidenciaxPedido.IsValidada = True
                        SaveEvidenciaxPedido.Observaciones = jParams['Comentarios']
                        SaveEvidenciaxPedido.FechaValidacion = datetime.datetime.now()
                        SaveEvidenciaxPedido.save()
                        SaveBanderaPedidoxviaje = XD_PedidosxViajes.objects.get(XD_IDPedido=SaveEvidenciaxPedido.IDXD_Pedido, XD_IDViaje=SaveEvidenciaxPedido.XD_IDViaje)
                        SaveBanderaPedidoxviaje.IsEvidenciaPedidoxViaje = True
                        SaveBanderaPedidoxviaje.IDUsuarioEvDigital = request.user.idusuario
                        SaveBanderaPedidoxviaje.FechaEvidenciaDigitalxPedidoxViaje = SaveEvidenciaxPedido.FechaValidacion
                        SaveBanderaPedidoxviaje.save()
                        IsXpress = XD_Viajes.objects.get(XD_IDViaje=SaveEvidenciaxPedido.XD_IDViaje) #IsViajeXpress(SaveEvidenciaxPedido.IDXD_Pedido, SaveEvidenciaxPedido.XD_IDViaje)
                        if IsXpress.TipoViaje == "XPRESS":
                            GetAllIDEvidenciasPedidos = XD_PedidosxViajes.objects.filter(XD_IDPedido=SaveEvidenciaxPedido.IDXD_Pedido)
                            for SaveEachPedidoPE in GetAllIDEvidenciasPedidos:
                                GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto=SaveEachPedidoPE.XD_IDPedido.XD_IDPedido).values('IDPendienteEnviar')
                                for VerificarTipoConcepto in GetIDPendientesEnviar:
                                    SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar=VerificarTipoConcepto['IDPendienteEnviar'])
                                    if SaveBanderaPendientesEnviar.TipoConcepto == 'PEDIDO':
                                        SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                                        SaveBanderaPendientesEnviar.save()
                        SaveXD_EDigital = EvidenciaDigitalCompleta("", SaveBanderaPedidoxviaje.XD_IDViaje.XD_IDViaje)
                        if SaveXD_EDigital:
                            SaveXD_EDigital = XD_Viajes.objects.get(XD_IDViaje=SaveBanderaPedidoxviaje.XD_IDViaje.XD_IDViaje)
                            SaveXD_EDigital.IsEvidenciaPedidos = True
                            SaveXD_EDigital.FechaEvidenciaDigital = datetime.datetime.now()
                            SaveXD_EDigital.save()
                            VerificarEvidenciaT1yT2 = GetAllEvidecesDigitalsT1yT2(SaveBanderaPedidoxviaje.XD_IDViaje.XD_IDViaje)
                            if VerificarEvidenciaT1yT2:
                                VerificarValidacionesEvidencias = VerificarSaveViajePE(SaveBanderaPedidoxviaje.XD_IDPedido.XD_IDPedido)
                                for EachViaje in VerificarValidacionesEvidencias:
                                    GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto=EachViaje).values('IDPendienteEnviar')
                                    for VerificarTipoConcepto in GetIDPendientesEnviar:
                                        SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar=VerificarTipoConcepto['IDPendienteEnviar'])
                                        if SaveBanderaPendientesEnviar.TipoConcepto == 'VIAJE':
                                            SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                                            SaveBanderaPendientesEnviar.save()
                    if jParams['TipoEvidencia'] == 'Maniobras' or jParams['TipoEvidencia'] == 'Custodia':
                        SaveEvidenciaxManiobra = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje=jParams['IDSaveEvidencia'])
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
                                    SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar=TC.IDPendienteEnviar.IDPendienteEnviar)
                                    if SaveBanderaPendientesEnviar.TipoConcepto == 'VIAJE':
                                        SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                                        SaveBanderaPendientesEnviar.save()
                    if jParams['TipoEvidencia'] == 'BKG':
                        SaveAprobarEvidencia = Bro_EvidenciasxViaje.objects.get(IDBro_EvidenciaxViaje=jParams['IDSaveEvidencia'])
                        SaveAprobarEvidencia.IsValidada = True
                        SaveAprobarEvidencia.Observaciones = jParams['Comentarios']
                        SaveAprobarEvidencia.FechaValidacion = datetime.datetime.now()
                        SaveAprobarEvidencia.IDUsuarioEvDigital = request.user.idusuario
                        SaveAprobarEvidencia.save()
                        SaveEvidenciaDigitalViaje = EvidenciaDigitalCompletaBKG("", SaveAprobarEvidencia.IDBro_Viaje.IDBro_Viaje)
                        if SaveEvidenciaDigitalViaje:
                            GetEvDViaje = Bro_Viajes.objects.get(IDBro_Viaje=SaveAprobarEvidencia.IDBro_Viaje.IDBro_Viaje)
                            GetEvDViaje.IsEvidenciasDigitales = True
                            GetEvDViaje.FechaRecEviDigitales = datetime.datetime.now()
                            GetEvDViaje.save()
                            GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.get(IDConcepto=SaveAprobarEvidencia.IDBro_Viaje.IDBro_Viaje)
                            GetEvDAdmon = PendientesEnviar.objects.get(IDPendienteEnviar=str(GetIDPendientesEnviar.IDPendienteEnviar))
                            GetEvDAdmon.IsEvidenciaDigital = True
                            GetEvDAdmon.save()
                    return HttpResponse(status=200)
    except Exception as e:
        print(e)
        transaction.rollback(using = 'XD_ViajesDB')
        transaction.rollback(using = 'bkg_viajesDB')
        transaction.rollback(using = 'users')
        return HttpResponse(status = 500)


def RechazarEvidencias(request):
    jParams = json.loads(request.body.decode('utf-8'))
    if jParams['TipoEvidencia'] == 'Pedido' or jParams['TipoEvidencia'] == 'Bitacora':
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
    AllEvidencesPedidosTrue = XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje)
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
    if "FTL" in Folio:
        GetEvidencias = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje=IDViaje, IsEvidenciaFisicaAprobada=0)
        for ComprobarEvidenciaFisica in GetEvidencias:
            TieneEvidenciasEnFalse.append(ComprobarEvidenciaFisica.IsValidada)
        if False in TieneEvidenciasEnFalse:
            pass
        else:
            for EVFisica in GetEvidencias:
                newEvidenciasFisicas = {}
                newEvidenciasFisicas["XD_IDPedido"] = EVFisica.IDBro_EvidenciaxViaje
                newEvidenciasFisicas["XD_IDViaje"] = EVFisica.IDBro_Viaje.IDBro_Viaje
                newEvidenciasFisicas["Delivery"] = "BKG-"+EVFisica.Titulo
                EvidenciaFisica.append(newEvidenciasFisicas)
    else:
        for TieneEvidenciaValidada in XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje=IDViaje, Titulo__in=('Maniobras de descarga', 'Maniobras de carga'), Tipo="MESA CONTROL") | Q(IDXD_Viaje=IDViaje, Tipo='EVCUSTODIAF')).values('IsValidada'):
            if len(TieneEvidenciaValidada) >= 1:
                TieneEvidenciasEnFalse.append(TieneEvidenciaValidada['IsValidada'])
        for TieneEvidenciaDigital in XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje).values('IsEvidenciaPedidoxViaje'):
            if len(TieneEvidenciaDigital) >= 1:
                TieneEvidenciasEnFalse.append(TieneEvidenciaDigital['IsEvidenciaPedidoxViaje'])
        if False in TieneEvidenciasEnFalse:
            pass
        else:
            VerificarTipoEvidencia = XD_Viajes.objects.get(XD_IDViaje = IDViaje)
            for delibery in XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, IsEvidenciaFisicaAprobada=0) if(VerificarTipoEvidencia.TipoViaje == 'CUSTODIA') else XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje):
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
                    if "BKG" in str(jParams["TipoEvidencia"]):
                        SaveEvFisica = Bro_EvidenciasxViaje.objects.get(IDBro_EvidenciaxViaje=jParams['IDPedido'])
                        SaveEvFisica.IsEvidenciaFisicaAprobada = True
                        SaveEvFisica.IDUsuarioEvFisica = request.user.idusuario
                        SaveEvFisica.FechaEvFisica = datetime.datetime.now()
                        SaveEvFisica.save()
                        allEvFisicaTrue = EvidenciaFisicaCompletaBKG(SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                        if allEvFisicaTrue:
                            SaveEvFisicaViajes = Bro_Viajes.objects.get(IDBro_Viaje=SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                            SaveEvFisicaViajes.IsEvidenciasFisicas = True
                            SaveEvFisicaViajes.FechaRecEviFisicas = datetime.datetime.now()
                            SaveEvFisicaViajes.save()
                            GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.get(IDConcepto=SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                            SaveEvFisicaAdmon = PendientesEnviar.objects.get(IDPendienteEnviar=str(GetIDPendientesEnviar.IDPendienteEnviar))
                            SaveEvFisicaAdmon.IsEvidenciaFisica = True
                            SaveEvFisicaAdmon.save()
                            #request.get("http://api-admon-demo.logistikgo.com/api/Usuarios/SaveFolioHojaLiberacion", params = {"IDConcepto":SaveEvFisica.IDBro_Viaje.IDBro_Viaje, "Proyecto":"BKG"})
                    else:
                        SaveEvidenciaPedidosxViaje = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje=jParams['IDPedido']) if(jParams["TipoEvidencia"] == 'FOLIO' or jParams["TipoEvidencia"] == 'CORREO') else XD_PedidosxViajes.objects.get(XD_IDPedido = jParams['IDPedido'], XD_IDViaje = jParams['IDViaje'])
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
    ClienteFiscal = XD_Viajes.objects.get(XD_IDViaje=IDViaje)
    TieneEvidenciaDigital = XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje)
    ListaTieneEvidenciaDigital = list()
    if ClienteFiscal.IDClienteFiscal != settings.IDCLIENTEFISCAL:
        for TieneEvi in TieneEvidenciaDigital:
            ListaTieneEvidenciaDigital.append(TieneEvi.IsEvidenciaPedidoxViaje)
    else:
        TieneEvidencia = XD_EvidenciasxPedido.objects.filter(XD_IDViaje=IDViaje)
        for EachEvidencia in TieneEvidencia:
            ListaTieneEvidenciaDigital.append(EachEvidencia.IsValidada)
    TieneEvidenciaManiobrasAll = XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje=IDViaje, Titulo__in = ('Maniobras de descarga', 'Maniobras de carga'), Tipo="MESA CONTROL") | Q(IDXD_Viaje=IDViaje, Tipo = 'EVCUSTODIAF'))
    for TieneEviManiobrasAll in TieneEvidenciaManiobrasAll:
        ListaTieneEvidenciaDigital.append(TieneEviManiobrasAll.IsValidada)
    IsEvidenciaDigitalCompleta = all(ListaTieneEvidenciaDigital)
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
                AddNewDataToJdon['IDViaje'] = Evidencias.IDBro_Viaje.IDBro_Viaje
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
    if len(PedidosWithEvDig) == 2:
        for i in PedidosWithEvDig:
            if i['XD_IDPedido'] == IDPedido and i['XD_IDViaje'] != ViajeID:
                ListaPedidosWithEvDig.append(i['IsEvidenciaDigital'])
        IsValido = False if( False in ListaPedidosWithEvDig) else True
    else:
        IsValido = False
    return IsValido

def VerificarSaveViajePE(IDPedido):
    GetIDViajes = XD_PedidosxViajes.objects.filter(XD_IDPedido=IDPedido)
    IDViajes = list()
    for Each in GetIDViajes:
        IDViajes.append(Each.XD_IDViaje.XD_IDViaje)
    return IDViajes

def GetAllEvidecesDigitalsT1yT2(IDViaje):
    GetPedidos = XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje)
    ListaPedidos = list()
    for i in GetPedidos:
        # a = XD_PedidosxViajes.objects.filter(XD_IDPedido = i.XD_IDPedido)
        # for j in a:
        ListaPedidos.append(i.IsEvidenciaPedidoxViaje)
    TrueORFALSE = False if False in ListaPedidos else True
    return TrueORFALSE


def DescargarHojaLiberacion(request):
    IDViaje = request.GET["IDViaje"]
    Proyecto = request.GET["Proyecto"]
    if Proyecto == 'BKG':
        try:
            GetRutaHojaLiberacion = Bro_Viajes.objects.get(IDBro_Viaje=IDViaje, IsEvidenciasDigitales=1, IsEvidenciasFisicas=1)
            if not GetRutaHojaLiberacion.IsDescargaHojaLiberacion or GetRutaHojaLiberacion.IsDescargaHojaLiberacion is None:
                HojaLiberacion = GetRutaHojaLiberacion.RutaHojaLiberacion
                if HojaLiberacion is not None:
                    GetRutaHojaLiberacion.IsDescargaHojaLiberacion = True
                    GetRutaHojaLiberacion.save()
            else:
                HojaLiberacion = False
            return JsonResponse({'HojaLiberacion': HojaLiberacion})
        except GetRutaHojaLiberacion.DoesNotExist:
            return HttpResponse(status=400)
        except Exception as e:
            return HttpResponse(status=500)
    else:
        try:
            GetRutaHojaLiberacion = XD_Viajes.objects.get(XD_IDViaje=IDViaje, IsEvidenciaPedidos=1, IsEvidenciaFisica=1)
            if not GetRutaHojaLiberacion.IsDescargaHojaLiberacion or GetRutaHojaLiberacion.IsDescargaHojaLiberacion is None:
                HojaLiberacion = GetRutaHojaLiberacion.RutaHojaEmbarqueCosto
                if HojaLiberacion is not None:
                    GetRutaHojaLiberacion.IsDescargaHojaLiberacion = True
                    GetRutaHojaLiberacion.save()
            else:
                HojaLiberacion = False
            # HojaLiberacion = GetRutaHojaLiberacion.RutaHojaEmbarqueCosto
            return JsonResponse({'HojaLiberacion': HojaLiberacion})
        except ObjectDoesNotExist:
            return HttpResponse(status=400)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

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
    return JsonResponse({"url":urlFile})


def descarga(IDViaje, Proyecto):
    sendAPI = CheckAllEvidenciaFisicaPedidoTrue(IDViaje) if Proyecto[:3] != "BKG" else CheckAllEvidenciaFisicaTrue(IDViaje)
    if sendAPI:
        Project = "BKG" if Proyecto[:3] == "BKG" else "XD"
        jsonParams = {'IDConcepto': IDViaje, 'Proyecto':Project}
        # respose = requests.post("http://api-admon.logistikgo.com/api/Usuarios/SaveFolioHojaLiberacion",
        #                         headers={'content-type': 'application/json'}, json=jsonParams)
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
            getEvidencias = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje=IDViaje)
            for evidencias in getEvidencias:
                jsonevidencias = {}
                jsonevidencias["Titulo"] = evidencias.Titulo
                jsonevidencias["RutaArchivo"] = evidencias.RutaArchivo
                ListEvidencias.append(jsonevidencias)
            return JsonResponse({"Evidencias": ListEvidencias})
        else:
            getEvidenciaxPedido = XD_EvidenciasxPedido.objects.filter(XD_IDViaje=IDViaje)
            for evidencias in getEvidenciaxPedido:
                jsonevidencias = {}
                TituloPedido = XD_PedidosxViajes.objects.get(XD_IDPedido=evidencias.IDXD_Pedido, XD_IDViaje=evidencias.XD_IDViaje)
                jsonevidencias["Titulo"] = TituloPedido.XD_IDPedido.Delivery if evidencias.Titulo != "BITACORA" else GetObservacionesByPedidoT1(TituloPedido.XD_IDPedido.Observaciones, "T1") if evidencias.Titulo == 'BITACORA' and TituloPedido.TipoTransporte == 'T1' else GetObservacionesByPedidoT1(TituloPedido.XD_IDPedido.Observaciones, "T2") if evidencias.Titulo == 'BITACORA' and TituloPedido.TipoTransporte == 'T2' else None
                jsonevidencias["RutaArchivo"] = evidencias.RutaArchivo
                ListEvidencias.append(jsonevidencias)
            getEvidenciaxCustodia= XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Tipo="EVCUSTODIAF", Titulo__in=('CORREO', 'FOLIO'))
            for evidenciasCustodias in getEvidenciaxCustodia:
                jsonevidencias = {}
                jsonevidencias["Titulo"] = evidenciasCustodias.Titulo
                jsonevidencias["RutaArchivo"] = evidenciasCustodias.RutaArchivo
                ListEvidencias.append(jsonevidencias)
            gerEvidenciasxManiobras = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Tipo__in=("MESA CONTROL", "EVIDENCIA ACCESORIOS"), Titulo__in=('Maniobras de carga', 'Maniobras de descarga'))
            for EvidenciasManiobras in gerEvidenciasxManiobras:
                jsonevidencias = {}
                jsonevidencias["Titulo"] = EvidenciasManiobras.Titulo
                jsonevidencias["RutaArchivo"] = EvidenciasManiobras.RutaArchivo
                ListEvidencias.append(jsonevidencias)
            return JsonResponse({"Evidencias": ListEvidencias})
    except Exception as e:
        print(e)
        return HttpResponse(status=500)




def GetObservacionesByPedidos(IDViaje):
    GetDelivery = XD_PedidosxViajes.objects.filter(XD_IDViaje=IDViaje)
    ListaObservaciones = list()
    for pedido in GetDelivery:
        if pedido.XD_IDPedido.IDClienteFiscal == settings.IDCLIENTEFISCAL:
            Observaciones = pedido.XD_IDPedido.Observaciones.split("-")
            delibery = Observaciones[0] if pedido.TipoTransporte == "T1" else Observaciones[
                1] if pedido.TipoTransporte == "T2" and len(Observaciones) == 2 else ""
            if delibery == "":
                pass
            else:
                datos = {}
                datos['XD_IDPedido'] = pedido.XD_IDPedido.XD_IDPedido
                datos['Delivery'] = delibery
                datos['IDViaje'] = pedido.XD_IDViaje.XD_IDViaje
                datos['TipoEvidencia'] = 'Bitacora'
                datos['RutaArchivo'] = ''
                datos['Status'] = 'Pendiente'
                datos['ComentarioRechazo'] = ''
                ListaObservaciones.append(datos)
    if len(ListaObservaciones) >= 1:
        unique = {each['Delivery']: each for each in ListaObservaciones}.values()
        ListaDepurada = list(unique)
        return ListaDepurada
    else:
        return ListaObservaciones


def GetObservacionesByPedidoT1(Observ,Tipo):
    Observaciones = Observ.split("-")
    if len(Observaciones) == 2:
        delibery = Observaciones[0] if Tipo == "T1" else Observaciones[
            1] if Tipo == "T2" else ""
    else:
        delibery = Observaciones[0] if Tipo == "T1" else ""
    return delibery


def GetEvidenciasMC(request):
    try:
        IDViaje = request.GET["IDViaje"]
        EvidenciaCorreo = list()
        if not XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Tipo='EVCUSTODIAF', Titulo='CORREO', IsEnviada=1).exists() or XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Tipo='EVCUSTODIAF', Titulo='CORREO', IsEnviada=1, IsRechazada=1).exists():
            XDFolio = XD_Viajes.objects.exclude(Status='CANCELADO').get(XD_IDViaje=IDViaje)
            data = XD_EvidenciasxViaje.objects.get(IDXD_Viaje=IDViaje, Tipo='EVCUSTODIAF', Titulo='CORREO', IsEnviada=1,IsRechazada = 1) if XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Tipo='EVCUSTODIAF', Titulo='CORREO', IsEnviada=1, IsRechazada = 1).exists() else ""
            newDelivery = {}
            newDelivery['XD_IDPedido'] = data.IDEvidenciaxViaje if XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Tipo='EVCUSTODIAF', Titulo='CORREO', IsEnviada=1, IsRechazada = 1).exists() else XDFolio.XD_IDViaje
            newDelivery['Delivery'] = XDFolio.Folio + "-" + "CORREO"
            newDelivery['IDViaje'] = XDFolio.XD_IDViaje
            newDelivery['TipoEvidencia'] = 'Custodia'
            newDelivery['RutaArchivo'] = ''
            newDelivery['Status'] = 'Rechazada' if XD_EvidenciasxViaje.objects.filter(IDXD_Viaje=IDViaje, Tipo='EVCUSTODIAF', Titulo='CORREO', IsEnviada=1, IsRechazada = 1).exists() else "Pendiente"
            newDelivery['ComentarioRechazo'] = ""
            EvidenciaCorreo.append(newDelivery)
            return JsonResponse({"Evidencias": EvidenciaCorreo})
        else:
            return HttpResponse(status=400)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)


def DownloadHojaLiberacion(request, **kwargs):
    IDViaje = kwargs.get('IDViaje', 0)
    Folio = kwargs.get('Folio', None)
    if Folio[:3] == "FTL" or Folio[:3] == "FTI":
        GetDatosViaje = Bro_Viajes.objects.get(IDBro_Viaje=IDViaje)
        if GetDatosViaje.IsEvidenciasDigitales and GetDatosViaje.IsEvidenciasFisicas and GetDatosViaje.IsDescargaHojaLiberacion and not Ext_Viajes_MesaControl.objects.filter(IDBro_Viaje=IDViaje, IsDescargaHojaLiberacionMC=True).exists() if request.user.roles == "MesaControl" else not Ext_Viajes_MesaControl.objects.filter(IDBro_Viaje=IDViaje, IsDescargaHojaLiberacionCXP=True).exists():
            URLHojaLiberacion = GetDatosViaje.RutaHojaLiberacion
            HojaLiberacion = urllib.request.urlopen(URLHojaLiberacion)
            response = HttpResponse(HojaLiberacion.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename="HojaLiberacion.pdf"'
            resp = SaveExtViajes(request, IDViaje, "BKG")
            return response if resp == 200 else resp
        else:
            resp = '<h2>La hoja de liberacion no cuenta con todas las validaciones para descargar</h2>'
            return HttpResponse(resp)
    elif Folio[:3] == "XDD":
        GetDatosViaje = XD_Viajes.objects.get(XD_IDViaje=IDViaje)
        if GetDatosViaje.IsEvidenciaPedidos and GetDatosViaje.IsEvidenciaFisica and GetDatosViaje.IsDescargaHojaLiberacion and not Ext_Viajes_MesaControlXD.objects.filter(XD_IDViaje=IDViaje, IsDescargaHojaLiberacionMC=True).exists() if request.user.roles == "MesaControl" else not Ext_Viajes_MesaControlXD.objects.filter(XD_IDViaje=IDViaje, IsDescargaHojaLiberacionCXP=True).exists():
            URLHojaLiberacion = GetDatosViaje.RutaHojaEmbarqueCosto
            HojaLiberacion = urllib.request.urlopen(URLHojaLiberacion)
            response = HttpResponse(HojaLiberacion.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename="HojaLiberacion.pdf"'
            resp = SaveExtViajes(request, IDViaje, "XD")
            return response if resp == 200 else resp
        else:
            resp = '<h2>La hoja de liberacion no cuenta con todas las validaciones para descargar</h2>'
            return HttpResponse(resp)
    else:
        resp = '<h2>Error al descargar la hoja de liberación</h2>'
        return HttpResponse(resp)


def SaveExtViajes(request, IDViaje, Proyecto):
    try:
        with transaction.atomic(using='bkg_viajesDB') if Proyecto == "BKG" else transaction.atomic(using='XD_ViajesDB'):
            if Proyecto == "BKG":
                SaveExtViajeMC = Ext_Viajes_MesaControl() if not Ext_Viajes_MesaControl.objects.filter(IDBro_Viaje=IDViaje).exists() else Ext_Viajes_MesaControl.objects.get(IDBro_Viaje=IDViaje)
                SaveExtViajeMC.IDBro_Viaje = Bro_Viajes.objects.get(IDBro_Viaje=IDViaje)
            else:
                SaveExtViajeMC = Ext_Viajes_MesaControlXD() if not Ext_Viajes_MesaControlXD.objects.filter(XD_IDViaje=IDViaje).exists() else Ext_Viajes_MesaControlXD.objects.get(XD_IDViaje=IDViaje)
                SaveExtViajeMC.XD_IDViaje = XD_Viajes.objects.get(XD_IDViaje=IDViaje)
            if request.user.roles == "CXP":
                SaveExtViajeMC.IDUsuarioCXP = AdmonUsuarios.objects.get(idusuario=request.user.idusuario)
                SaveExtViajeMC.IsDescargaHojaLiberacionCXP = True
                SaveExtViajeMC.FechaDescargaHojaLiberacionCXP = datetime.datetime.now()
                SaveExtViajeMC.save()
                return 200
            elif request.user.roles == "MesaControl":
                SaveExtViajeMC.IDUsuarioMC = AdmonUsuarios.objects.get(idusuario=request.user.idusuario)
                SaveExtViajeMC.IsDescargaHojaLiberacionMC = True
                SaveExtViajeMC.FechaDescargaHojaLiberacionMC = datetime.datetime.now()
                SaveExtViajeMC.save()
                return 200
            else:
                resp = '<h2>Ocurrio un error descargando la hoja de liberacion</h2>'
                return HttpResponse(resp)
    except Exception as e:
        print(e)
        transaction.rollback(using='bkg_viajesDB') if Proyecto == "BKG" else transaction.rollback(using='XD_ViajesDB')
        resp = '<h2>Ocurrio un error descargando la hoja de liberacion, por favor intente de nuevo</h2>'
        return HttpResponse(resp)

def ValidacionEviByObservaciones(XD_IDViaje):
    GetTotalEvi = GetObservacionesByPedidos(XD_IDViaje)
    if len(GetTotalEvi) >= 1:
        TotalEvidencias = list()
        for eachEvi in GetTotalEvi:
            TotalEvidencias.append(True if XD_EvidenciasxPedido.objects.filter(XD_IDViaje=eachEvi["IDViaje"],
                                                       IDXD_Pedido=eachEvi["XD_IDPedido"],
                                                       Titulo='BITACORA').exists() else False)
        return all(TotalEvidencias)
    else:
        return False



def CountTotalEvidencias(Pedidos):
    CountList = list()
    if Pedidos[0].XD_IDViaje.IDClienteFiscal == settings.IDCLIENTEFISCAL:
        for eachPedido in Pedidos:
            observaciones = {}
            observaciones["name"] = GetObservacionesByPedidoT1(eachPedido.XD_IDPedido.Observaciones, eachPedido.TipoTransporte)
            "" if observaciones["name"] == '' or observaciones["name"] == None or observaciones["name"] == [] else CountList.append(observaciones)
        return len(CountList)
    else:
        return 0
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from XD_Viajes.models import XD_Viajes, XD_PedidosxViajes, XD_Pedidos, XD_AccesoriosxViajes, XD_EvidenciasxPedido, XD_EvidenciasxViaje
from PendientesEnviar.models import PendientesEnviar, RelacionConceptoxProyecto
from usersadmon.models import AdmonUsuarios
from bkg_viajes.models import Bro_Viajes, Bro_EvidenciasxViaje
import json, datetime
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json
from itertools import chain
import requests

@login_required
def EvidenciasProveedor(request):
    if request.user.roles != 'Proveedor':
        EvidenciasxAprobar = XD_Viajes.objects.filter(Status = 'FINALIZADO').exclude(Status = 'CANCELADO')
        EvidenciasxAprobarBKG = Bro_Viajes.objects.filter(StatusProceso = 'FINALIZADO').exclude(StatusProceso = 'CANCELADO')
        Evidencias = chain(EvidenciasxAprobar, EvidenciasxAprobarBKG)
        SinEvidenciaDigitalXD = XD_Viajes.objects.filter(IsEvidenciaPedidos = False).count()
        SinEvidenciaDigitalBKG = Bro_Viajes.objects.filter(IsEvidenciasDigitales = False).count()
        SinEvidenciaDigital = SinEvidenciaDigitalXD+SinEvidenciaDigitalBKG
        return render(request, 'EvidenciasProveedor.html', {'EvidenciasxAprobar': Evidencias, 'EvidenciaDigital': SinEvidenciaDigital})
    elif request.user.roles == 'Proveedor':
        # SinEvidenciaDigital = XD_Viajes.objects.filter(IsEvidencia = False).count()
        # SinEvidenciaFisica = XD_Viajes.objects.filter(IsEvidenciaFisica = False).count()
        return render(request, 'EvidenciasProveedor.html')

def FindFolioProveedor(request):
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
                        arrFoliosEvidencias.append(newDelivery)
            else:
                GetDelivery = XD_PedidosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje, StatusPedido = 'ENTREGADO')#, StatusPedido = 'ENTREGADO')
                if GetDelivery:
                    for Delivery in GetDelivery:
                        if len(XD_EvidenciasxPedido.objects.filter(IDXD_Pedido = Delivery.XD_IDPedido.XD_IDPedido, XD_IDViaje = Delivery.XD_IDViaje.XD_IDViaje)) >= 1:
                            TieneEvidencia = XD_EvidenciasxPedido.objects.get(IDXD_Pedido = Delivery.XD_IDPedido.XD_IDPedido, XD_IDViaje = Delivery.XD_IDViaje.XD_IDViaje)
                            newDelivery = {}
                            newDelivery['XD_IDPedido'] = Delivery.XD_IDPedido.XD_IDPedido
                            newDelivery['Delivery'] = Delivery.XD_IDPedido.Delivery
                            newDelivery['IDViaje'] = Delivery.XD_IDViaje.XD_IDViaje
                            newDelivery['TipoEvidencia'] = 'Pedido'
                            newDelivery['RutaArchivo'] = '' if(TieneEvidencia.IsEnviada and TieneEvidencia.IsRechazada ) else TieneEvidencia.RutaArchivo
                            newDelivery['Status'] = 'Rechazada' if(TieneEvidencia.IsEnviada and TieneEvidencia.IsRechazada) else 'Aprobada' if(TieneEvidencia.IsValidada) else  "Enviada" if (TieneEvidencia.IsEnviada and not TieneEvidencia.IsRechazada and not TieneEvidencia.IsValidada) else "Otro"
                            arrFoliosEvidencias.append(newDelivery)
                        else:
                            newDelivery = {}
                            newDelivery['XD_IDPedido'] = Delivery.XD_IDPedido.XD_IDPedido
                            newDelivery['Delivery'] = Delivery.XD_IDPedido.Delivery
                            newDelivery['IDViaje'] = Delivery.XD_IDViaje.XD_IDViaje
                            newDelivery['TipoEvidencia'] = 'Pedido'
                            newDelivery['RutaArchivo'] = "" if(GetDelivery[0].IsEvidenciaPedidoxViaje == 1 or GetDelivery[0].IsEvidenciaFisicaPedidoxViaje == 1) else ""
                            newDelivery['Status'] = 'Otro' if(GetDelivery[0].IsEvidenciaPedidoxViaje == 1 or GetDelivery[0].IsEvidenciaFisicaPedidoxViaje == 1) else 'Pendiente'
                            arrFoliosEvidencias.append(newDelivery)
            for Maniobras in XD_AccesoriosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje, Descripcion__in = ('Maniobras de descarga', 'Maniobras de carga')):
                if Maniobras:
                    GetManiobras = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje = Maniobras.XD_IDViaje, Titulo__in = ('Maniobras de descarga', 'Maniobras de carga'))
                    for GetEachManiobra in GetManiobras:
                        newDelivery = {}
                        newDelivery['XD_IDPedido'] = Maniobras.XD_IDAccesorioxViaje if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada or len(GetManiobras) ==0) else  GetEachManiobra.IDEvidenciaxViaje
                        newDelivery['Delivery'] = Maniobras.Descripcion if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada or len(GetManiobras) >= 1) else  GetEachManiobra.Titulo
                        newDelivery['IDViaje'] = Maniobras.XD_IDViaje if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada or len(GetManiobras) >= 1) else GetEachManiobra.IDXD_Viaje
                        newDelivery['TipoEvidencia'] = 'Maniobras'
                        newDelivery['RutaArchivo'] = '' if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else GetEachManiobra.RutaArchivo if (GetEachManiobra.IsEnviada and not GetEachManiobra.IsRechazada and not GetEachManiobra.IsValidada) else GetEachManiobra.RutaArchivo
                        newDelivery['Status'] = 'Rechazada' if(GetEachManiobra.IsEnviada and GetEachManiobra.IsRechazada) else 'Aprobada' if(GetEachManiobra.IsEnviada and GetEachManiobra.IsValidada) else 'Pendiente' if len(GetManiobras) == 0 else "Enviada" if (GetEachManiobra.IsEnviada and not GetEachManiobra.IsRechazada and not GetEachManiobra.IsValidada) else "Otro"
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
                        SaveEvidenciasxBKG.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
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
                        print("yes")
                        SaveEvidenciaBKG = Bro_EvidenciasxViaje()
                        SaveEvidenciaBKG.IDBro_Viaje = Bro_Viajes.objects.get(IDBro_Viaje = Evidencias['IDViaje'])
                        SaveEvidenciaBKG.FechaCaptura = datetime.datetime.now()
                        SaveEvidenciaBKG.Titulo = Evidencias['Titulo']
                        SaveEvidenciaBKG.Tipo = 'EVIDENCIA'
                        SaveEvidenciaBKG.NombreArchivo = Evidencias['NombreArchivo']
                        SaveEvidenciaBKG.RutaArchivo = Evidencias['Evidencia']
                        SaveEvidenciaBKG.IsEnviada = True
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
                        SaveEvidenciaxPedido.Tipo = 'EVIDENCIA' if(Evidencias['TipoEvidencia'] == 'Pedido') else 'EVIDENCIA ACCESORIOS' if(Evidencias['TipoEvidencia'] == 'Maniobras') else "EVCUSTODIAF" if(Evidencias['TipoEvidencia'] == 'Custodia') else ""
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
                    AddEvidencia['Delivery'] = GetDelivery.Delivery
                    AddEvidencia['TipoEvidencia'] = 'Pedido'
                    AddEvidencia['IDViaje'] = GetEvidenciaxPedido.XD_IDViaje
                    ListEvidencias.append(AddEvidencia)
            GetEvidenciasxViaje = XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga','Maniobras de carga')) | Q(IDXD_Viaje = IDViaje, Tipo = 'EVCUSTODIAF'))
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
                        SaveBanderaPedidoxviaje.save()
                        IsXpress = IsViajeXpress(SaveEvidenciaxPedido.IDXD_Pedido, SaveEvidenciaxPedido.XD_IDViaje)
                        if IsXpress:
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
                        SaveEvidenciaxManiobra.save()
                            # if jParams['TipoEvidencia'] == 'Custodia': #las maniobras no se guardan la evidencia digital como bandera en cxp o cxc
                            #     GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto = SaveEvidenciaxManiobra.IDXD_Viaje)
                            #     SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar = GetIDPendientesEnviar[0].IDPendienteEnviar.IDPendienteEnviar)
                            #     SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                            #     SaveBanderaPendientesEnviar.save()
                        SaveXD_EDigital = EvidenciaDigitalCompleta("",SaveEvidenciaxManiobra.IDXD_Viaje)
                        if SaveXD_EDigital:
                            SaveXD_EDigital = XD_Viajes.objects.get(XD_IDViaje = SaveEvidenciaxManiobra.IDXD_Viaje)
                            SaveXD_EDigital.IsEvidenciaPedidos = True
                            SaveXD_EDigital.save()
                            if jParams['TipoEvidencia'] == 'Custodia':
                                GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto = SaveXD_EDigital.XD_IDViaje).values('IDPendienteEnviar')
                                for TC in GetIDPendientesEnviar:
                                    SaveBanderaPendientesEnviar = PendientesEnviar.objects.get(IDPendienteEnviar = TC['IDPendienteEnviar'])
                                    if SaveBanderaPendientesEnviar['TipoConcepto'] == 'VIAJE':
                                        SaveBanderaPendientesEnviar.IsEvidenciaDigital = True
                                        SaveBanderaPendientesEnviar.save()
                    if jParams['TipoEvidencia'] == 'BKG':
                        SaveAprobarEvidencia = Bro_EvidenciasxViaje.objects.get(IDBro_EvidenciaxViaje = jParams['IDSaveEvidencia'])
                        SaveAprobarEvidencia.IsValidada = True
                        SaveAprobarEvidencia.Observaciones = jParams['Comentarios']
                        SaveAprobarEvidencia.FechaValidacion = datetime.datetime.now()
                        SaveAprobarEvidencia.save()
                        SaveEvidenciaDigitalViaje = EvidenciaDigitalCompletaBKG("",SaveAprobarEvidencia.IDBro_Viaje.IDBro_Viaje)
                        if SaveEvidenciaDigitalViaje:
                            GetEvDViaje = Bro_Viajes.objects.get(IDBro_Viaje = SaveAprobarEvidencia.IDBro_Viaje.IDBro_Viaje)
                            GetEvDViaje.IsEvidenciasDigitales = True
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
        RechazarEvidenciaxPedido.FechaRechazo = datetime.datetime.now()
        RechazarEvidenciaxPedido.save()
    elif jParams['TipoEvidencia'] == 'Maniobras' or jParams['TipoEvidencia'] == 'Custodia':
        RechazarEvidenciaManiobra = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje = jParams['IDRechazarEvidencia'])
        RechazarEvidenciaManiobra.IsRechazada = True
        RechazarEvidenciaManiobra.Observaciones = jParams['Comentarios']
        RechazarEvidenciaManiobra.ComentarioRechazo = jParams['ComentarioRechazo']
        RechazarEvidenciaManiobra.FechaRechazo = datetime.datetime.now()
        RechazarEvidenciaManiobra.save()
    elif jParams['TipoEvidencia'] == "BKG":
        RechazarEvidenciaBKG = Bro_EvidenciasxViaje.objects.get(IDBro_EvidenciaxViaje = jParams['IDRechazarEvidencia'])
        RechazarEvidenciaBKG.IsRechazada = True
        RechazarEvidenciaBKG.Observaciones = jParams['Comentarios']
        RechazarEvidenciaBKG.ComentarioRechazo = jParams['ComentarioRechazo']
        RechazarEvidenciaBKG.FechaRechazo = datetime.datetime.now()
        RechazarEvidenciaBKG.save()
    return HttpResponse("")


def ValidarEvidenciaXD_Viajea(IDViaje):
    AllEvidencesPedidosTrue = XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje)
    listEvidenciasBool = list()
    for a in AllEvidencesPedidosTrue:
        listEvidenciasBool.append(a.IsEvidenciaPedidoxViaje,)
        listEvidenciasBool.append(a.IsEvidenciaFisicaPedidoxViaje,)
    AllEvidencesManiobrasTrue = XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga','Maniobras de carga')) | Q(IDXD_Viaje = IDViaje, Tipo = 'EVCUSTODIAF'))
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
        for TieneEvidenciaValidada in XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga', 'Maniobras de carga')) | Q (IDXD_Viaje = IDViaje, Tipo = 'EVCUSTODIAF')).values('IsValidada'):
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
                        SaveEvFisica.save()
                        allEvFisicaTrue = EvidenciaFisicaCompletaBKG(SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                        if allEvFisicaTrue:
                            SaveEvFisicaViajes = Bro_Viajes.objects.get(IDBro_Viaje = SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                            SaveEvFisicaViajes.IsEvidenciasFisicas = True
                            SaveEvFisicaViajes.save()
                            GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.get(IDConcepto = SaveEvFisica.IDBro_Viaje.IDBro_Viaje)
                            SaveEvFisicaAdmon = PendientesEnviar.objects.get(IDPendienteEnviar = str(GetIDPendientesEnviar.IDPendienteEnviar))
                            SaveEvFisicaAdmon.IsEvidenciaFisica = True
                            SaveEvFisicaAdmon.save()
                    else:
                        SaveEvidenciaPedidosxViaje = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje = jParams['IDPedido']) if(jParams["TipoEvidencia"] == 'FOLIO' or jParams["TipoEvidencia"] == 'CORREO') else XD_PedidosxViajes.objects.get(XD_IDPedido = jParams['IDPedido'], XD_IDViaje = jParams['IDViaje'])
                        if jParams["TipoEvidencia"] == 'FOLIO' or jParams["TipoEvidencia"] == 'CORREO':
                            SaveEvidenciaPedidosxViaje.IsEvidenciaFisicaAprobada = True
                        else:
                            SaveEvidenciaPedidosxViaje.IsEvidenciaFisicaPedidoxViaje = True
                        SaveEvidenciaPedidosxViaje.save()
                        if jParams["TipoEvidencia"] != 'FOLIO' or jParams["TipoEvidencia"] != 'CORREO':
                            IsExpress = XD_Viajes.objects.get(XD_IDViaje = jParams['IDViaje'])
                            if IsExpress.TipoViaje == 'XPRESS':
                                GetIDPE = RelacionConceptoxProyecto.objects.filter(IDConcepto = jParams['IDPedido']).values("IDPendienteEnviar")
                                for Conceptos in GetIDPE:
                                    SaveEVFisPE = PendientesEnviar.objects.get(IDPendienteEnviar = Conceptos["IDPendienteEnviar"])
                                    if SaveEVFisPE.TipoConcepto == 'PEDIDO':
                                        SaveEVFisPE.IsEvidenciaFisica = True
                                        SaveEVFisPE.save()
                        SaveXD_Viajes = ValidarEvidenciaXD_Viajea(jParams['IDViaje'])
                        if SaveXD_Viajes:
                            SaveBanderasXD_Viajes = XD_Viajes.objects.get(XD_IDViaje = jParams['IDViaje'])
                            SaveBanderasXD_Viajes.IsEvidenciaFisica = True
                            SaveBanderasXD_Viajes.Status = 'COMPLETO'
                            SaveBanderasXD_Viajes.save()
                            GetIDPendientesEnviar = RelacionConceptoxProyecto.objects.filter(IDConcepto = jParams['IDViaje']).values('IDPendienteEnviar')
                            for conceptos in GetIDPendientesEnviar:
                                SaveEvFisicaAdmon = PendientesEnviar.objects.get(IDPendienteEnviar = conceptos['IDPendienteEnviar'])
                                if SaveEvFisicaAdmon.TipoConcepto == 'VIAJE':
                                    SaveEvFisicaAdmon.IsEvidenciaFisica = True
                                    SaveEvFisicaAdmon.save()
                    return HttpResponse(status = 200)
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
    TieneEvidenciaManiobrasAll = XD_EvidenciasxViaje.objects.filter(Q(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga', 'Maniobras de carga')) | Q(IDXD_Viaje = IDViaje, Tipo = 'EVCUSTODIAF'))
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
    for i  in GetPedidos:
        a = XD_PedidosxViajes.objects.filter(XD_IDPedido = i.XD_IDPedido)
        for j in a:
            ListaPedidos.append(j.IsEvidenciaPedidoxViaje)
    TrueORFALSE = False if False in ListaPedidos else True
    print(TrueORFALSE)
    return TrueORFALSE


def DescargarHojaLiberacion(request):
    IDViaje = request.GET["IDViaje"]
    Proyecto = request.GET["Proyecto"]
    if Proyecto == 'BKG':
        GetRutaHojaLiberacion = Bro_Viajes.objects.get(IDBro_Viaje = IDViaje)
        HojaLiberacion = GetRutaHojaLiberacion.RutaHojaLiberacion
    else:
        GetRutaHojaLiberacion = XD_Viajes.objects.get(XD_IDViaje = IDViaje)
        HojaLiberacion = GetRutaHojaLiberacion.RutaHojaEmbarqueCosto
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

    # try:
    #     if GetTipoViaje.TipoViaje == 'XPRESS':
    #         GetPedidosXpress = XD_PedidosxViajes.filter(XD_IDViaje = GetTipoViaje.XD_IDViaje, IsEvidenciaPedidoxViaje = 1)
    #         for EachPedido in GetPedidosXpress:
    #             PedidosWithEvDig.append(EachPedido.IsEvidenciaPedidoxViaje)
    #         IsValido = False if( False in PedidosWithEvDig) else True
    #         return IsValido
    # except Exception as e:
    #     print(e)
    #     return False
# hojaembaruecosto --> xd hoja liberacion

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from XD_Viajes.models import XD_Viajes, XD_PedidosxViajes, XD_Pedidos, XD_AccesoriosxViajes, XD_EvidenciasxPedido, XD_EvidenciasxViaje
from usersadmon.models import AdmonUsuarios
import json, datetime
from django.db import transaction

def EvidenciasProveedor(request):
    if request.user.roles != 'Proveedor':
        EvidenciasxAprobar = XD_Viajes.objects.filter(IsEvidenciaPedidos = 0, IsEvidenciaFisica = 0).exclude(Status = 'CANCELADO')
        return render(request, 'EvidenciasProveedor.html', {'EvidenciasxAprobar': EvidenciasxAprobar})
    elif request.user.roles == 'Proveedor':
        SinEvidenciaDigital = XD_Viajes.objects.filter(IsEvidencia = False).count()
        SinEvidenciaFisica = XD_Viajes.objects.filter(IsEvidenciaFisica = False).count()
        return render(request, 'EvidenciasProveedor.html', {'EvidenciaDigital': SinEvidenciaDigital, 'EvidenciaFisica': SinEvidenciaFisica, 'Rol': request.user.roles})

def FindFolioProveedor(request):
    Folio = request.GET["Folio"]
    arrFoliosEvidencias = list()
    try:
        XDFolio = XD_Viajes.objects.exclude(Status = 'CANCELADO').get(Folio = Folio, IsEvidenciaPedidos = 0, IsEvidenciaFisica = 0)
        GetDelivery = XD_PedidosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje)
        if GetDelivery:
            for Delivery in GetDelivery:
                if XD_EvidenciasxPedido.objects.filter(IDXD_Pedido = Delivery.XD_IDPedido.XD_IDPedido, XD_IDViaje = Delivery.XD_IDViaje.XD_IDViaje).exists():
                    TieneEvidencia = XD_EvidenciasxPedido.objects.get(IDXD_Pedido = Delivery.XD_IDPedido.XD_IDPedido, XD_IDViaje = Delivery.XD_IDViaje.XD_IDViaje)
                    newDelivery = {}
                    newDelivery['XD_IDPedido'] = Delivery.XD_IDPedido.XD_IDPedido
                    newDelivery['Delivery'] = Delivery.XD_IDPedido.Delivery
                    newDelivery['IDViaje'] = Delivery.XD_IDViaje.XD_IDViaje
                    # newDelivery['Estatus'] = "Enviada" if (TieneEvidencia.IsEnviada) else "Pendiente"
                    arrFoliosEvidencias.append(newDelivery)
                else:
                    newDelivery = {}
                    newDelivery['XD_IDPedido'] = Delivery.XD_IDPedido.XD_IDPedido
                    newDelivery['Delivery'] = Delivery.XD_IDPedido.Delivery
                    newDelivery['IDViaje'] = Delivery.XD_IDViaje.XD_IDViaje
                    newDelivery['Estatus'] = "Pendiente"
                    arrFoliosEvidencias.append(newDelivery)

        else:
            arrFoliosEvidencias.append(XDFolio.Folio)
        for Maniobras in XD_AccesoriosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje).values_list("Descripcion", flat=True):
            if Maniobras == 'Maniobras de descarga' or Maniobras == 'Maniobras de carga':
                arrFoliosEvidencias.append(Maniobras)
        print(arrFoliosEvidencias)
        return JsonResponse({'Found': True, 'Folios': arrFoliosEvidencias})
    except Exception as e:
        print(e)
        return JsonResponse({'Found': False})

def SaveEvidencias(request):
    jParams = json.loads(request.body.decode('utf-8'))
    for Evidencias in jParams['arrEvidencias']:
        SaveEvidenciaxPedido = XD_EvidenciasxPedido()
        SaveEvidenciaxPedido.IDXD_Pedido = Evidencias['IDPedido']
        SaveEvidenciaxPedido.XD_IDViaje = Evidencias['IDViaje']
        SaveEvidenciaxPedido.IDUsuarioAlta = AdmonUsuarios.objects.get(idusuario = request.user.idusuario)
        SaveEvidenciaxPedido.FechaCaptura = datetime.datetime.now()
        SaveEvidenciaxPedido.Titulo = 'EVIDENCIA1'
        SaveEvidenciaxPedido.Tipo = 'EVIDENCIA'
        SaveEvidenciaxPedido.NombreArchivo = 'dd.pdf'
        SaveEvidenciaxPedido.RutaArchivo = Evidencias['Evidencia']
        SaveEvidenciaxPedido.Observaciones = ''
        SaveEvidenciaxPedido.IsEnviada = 1
        SaveEvidenciaxPedido.save()
    return HttpResponse('')

def GetEvidenciasMesaControl(request):
    IDViaje = request.GET["XD_IDViaje"]
    try:
        GetIDPedidos = XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje).values('XD_IDPedido')
        # ListEvi= EvidenciasToList(GetIDPedidos)
        ListEvidencias = list()
        for GetPedidos in GetIDPedidos:
            GetDelivery = XD_Pedidos.objects.get(XD_IDPedido = GetPedidos['XD_IDPedido'])
            GetEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDXD_Pedido = GetPedidos['XD_IDPedido'], XD_IDViaje = IDViaje)
            if GetEvidenciaxPedido.IsEnviada and GetEvidenciaxPedido.IsValidada == 0:
                AddEvidencia = {}
                AddEvidencia['IDEvidencia'] = GetEvidenciaxPedido.IDEvidenciaxPedido
                AddEvidencia['URLEvidencia'] = GetEvidenciaxPedido.RutaArchivo
                AddEvidencia['Delivery'] = GetDelivery.Delivery
                AddEvidencia['TipoEvidencia'] = 'Pedido'
                AddEvidencia['IDViaje'] = GetEvidenciaxPedido.XD_IDViaje
                ListEvidencias.append(AddEvidencia)
        GetEvidenciasxViaje = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje = IDViaje)
        ListEvi = EvidenciasToList(GetEvidenciasxViaje)
        for Maniobras in ListEvi:
            if Maniobras['Titulo'] == 'Maniobras de descarga' or Maniobras['Titulo'] == 'Maniobras de carga':
                AddManiobras = {}
                AddManiobras["IDEvidencia"] = Maniobras['IDEvidenciaxViaje']
                AddManiobras['URLEvidencia'] = Maniobras['RutaArchivo']
                AddManiobras['Delivery'] = Maniobras['Titulo']
                AddManiobras['TipoEvidencia'] = Maniobras['TipoEvidencia']
                AddManiobras['IDViaje'] = Maniobras['IDXD_Viaje']
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
        Delivery["TipoEvidencia"] = 'Maniobras'
        ListEvi.append(Delivery)
    return ListEvi

def SaveAprobarEvidencia(request):
    jParams = json.loads(request.body.decode('utf-8'))
    if jParams['TipoEvidencia'] == 'Pedido':
        try:
            with transaction.atomic(using = 'XD_ViajesDB'):
                SaveEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDEvidenciaxPedido = jParams['IDSaveEvidencia'])
                SaveEvidenciaxPedido.IsValidada = True
                SaveEvidenciaxPedido.Observaciones = jParams['Comentarios']
                SaveEvidenciaxPedido.save()
                SaveBanderaPedidoxviaje = XD_PedidosxViajes.objects.get(XD_IDPedido = SaveEvidenciaxPedido.IDXD_Pedido, XD_IDViaje = SaveEvidenciaxPedido.XD_IDViaje)
                SaveBanderaPedidoxviaje.IsEvidenciaPedidoxViaje = True
                SaveBanderaPedidoxviaje.save()
                SaveXD_Viajes = ValidarEvidenciaXD_Viajea(SaveBanderaPedidoxviaje.XD_IDViaje)
                if SaveXD_Viajes:
                    SaveBanderasXD_Viajes = XD_Viajes.object.get(XD_IDViaje = SaveBanderaPedidoxviaje.XD_IDViaje)
                    SaveBanderasXD_Viajes.IsEvidenciaPedidos = True
                    SaveBanderasXD_Viajes.IsEvidenciaFisica = True
                    SaveBanderasXD_Viajes.save()
                return HttpResponse(status = 200)
        except Exception as e:
            print(e)
            transaction.rollback(using = 'XD_ViajesDB')
            return HttpResponse(status = 500)
    elif jParams['TipoEvidencia'] == 'Maniobras':
        try:
            with transaction.atomic(using = 'XD_ViajesDB'):
                SaveEvidenciaxManiobra = XD_EvidenciasxViaje.objects.get(IDEvidenciaxViaje = jParams['IDSaveEvidencia'])
                SaveEvidenciaxManiobra.IsValidada = True
                SaveEvidenciaxManiobra.Observaciones = jParams['Comentarios']
                SaveEvidenciaxManiobra.save()
                SaveXD_Viajes = ValidarEvidenciaXD_Viajea(SaveEvidenciaxManiobra.XD_IDViaje)
                if SaveXD_Viajes:
                    SaveBanderasXD_Viajes = XD_Viajes.object.get(XD_IDViaje = SaveEvidenciaxManiobra.XD_IDViaje)
                    SaveBanderasXD_Viajes.IsEvidenciaPedidos = True
                    SaveBanderasXD_Viajes.IsEvidenciaFisica = True
                    SaveBanderasXD_Viajes.save()
                return HttpResponse(status = 200)
        except Exception as e:
            print(e)
            transaction.rollback(using = 'XD_ViajesDB')
            return HttpResponse(status = 500)



def RechazarEvidencias(request):
    jParams = json.loads(request.body.decode('utf-8'))
    if jParams['TipoEvidencia'] == 'Pedido':
        RechazarEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDEvidenciaxPedido = jParams['IDSaveEvidencia'])
        RechazarEvidenciaxPedido.IsRechazada = True
        RechazarEvidenciaxPedido.Observaciones = jParams['Comentarios']
        RechazarEvidenciaxPedido.save()
    return HttpResponse("")

def ValidarEvidenciaXD_Viajea(IDViaje):
    AllEvidencesPedidosTrue = XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje)
    ListEvi= list()
    for NewEvidencia in AllEvidencesPedidosTrue:
        Delivery = {}
        Delivery["XD_IDPedido"] = NewEvidencia.XD_IDPedido
        Delivery["XD_IDViaje"] = NewEvidencia.XD_IDViaje
        Delivery["IsEvidenciaPedidoxViaje"] =NewEvidencia.IsEvidenciaPedidoxViaje
        Delivery["IsEvidenciaFisicaPedidoxViaje"] = NewEvidencia.IsEvidenciaFisicaPedidoxViaje
        Delivery["TipoEvidencia"] = 'Maniobras'
        ListEvi.append(Delivery)
    listEvidenciasBool = list()
    for a in ListEvi:
        listEvidenciasBool.append(a['IsEvidenciaPedidoxViaje'],)
        listEvidenciasBool.append(a['IsEvidenciaFisicaPedidoxViaje'],)
    AllEvidencesManiobrasTrue = XD_EvidenciasxViaje.objects.filter(IDXD_Viaje = IDViaje)
    listEvidenciasManiobrasBool = list()
    if AllEvidencesManiobrasTrue:
        ListEvixViaje= list()
        for newList in AllEvidencesManiobrasTrue:
            ListEvidenciasxViaje = {}
            ListEvidenciasxViaje["IDXD_Viaje"] = newList.IDXD_Viaje
            ListEvidenciasxViaje["IsValidada"] = newList.IsValidada
            ListEvixViaje.append(ListEvidenciasxViaje)
        for b in ListEvixViaje:
            listEvidenciasManiobrasBool.append(b["IsValidada"])
    else:
        listEvidenciasManiobrasBool.append('')
    Accept = False if(False in listEvidenciasBool or False in listEvidenciasManiobrasBool) else True
    print(Accept)
    return Accept


def GetEvidenciaFisica(request):
    IDViaje = request.GET["XD_IDViaje"]
    EvidenciaFisica = list()
    TieneEvidenciasEnFalse = list()
    for TieneEvidenciaValidada in XD_EvidenciasxViaje.objects.filter(IDXD_Viaje = IDViaje, Titulo__in = ('Maniobras de descarga', 'Maniobras de carga')).values('IsValidada'):
        if TieneEvidenciaValidada:
            TieneEvidenciasEnFalse.append(TieneEvidenciaValidada['IsValidada'])
    for TieneEvidenciaDigital in XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje).values('IsEvidenciaPedidoxViaje'):
        if TieneEvidenciaDigital:
            TieneEvidenciasEnFalse.append(['IsEvidenciaPedidoxViaje'])
    if False in TieneEvidenciasEnFalse:
        pass
    else:
        for delibery in XD_PedidosxViajes.objects.filter(XD_IDViaje = IDViaje):
            newEvidenciasFisicas = {}
            newEvidenciasFisicas["XD_IDPedido"] = delibery.XD_IDPedido.XD_IDPedido
            newEvidenciasFisicas["XD_IDViaje"] = delibery.XD_IDViaje.XD_IDViaje
            newEvidenciasFisicas["Delivery"] = delibery.XD_IDPedido.Delivery
            EvidenciaFisica.append(newEvidenciasFisicas)
    return JsonResponse({'EvidenciaFisica': EvidenciaFisica})

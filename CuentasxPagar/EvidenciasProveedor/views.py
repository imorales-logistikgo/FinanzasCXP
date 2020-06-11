from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from XD_Viajes.models import XD_Viajes, XD_PedidosxViajes, XD_Pedidos, XD_AccesoriosxViajes, XD_EvidenciasxPedido
from usersadmon.models import AdmonUsuarios
import json, datetime

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
            if GetEvidenciaxPedido.IsEnviada:
                AddEvidencia = {}
                AddEvidencia['IDEvidencia'] = GetEvidenciaxPedido.IDEvidenciaxPedido
                AddEvidencia['URLEvidencia'] = GetEvidenciaxPedido.RutaArchivo
                AddEvidencia['Delivery'] = GetDelivery.Delivery
                AddEvidencia['TipoEvidencia'] = 'Pedido'
                ListEvidencias.append(AddEvidencia)
        # for Maniobras in XD_AccesoriosxViajes.objects.filter(XD_IDViaje = IDViaje).values_list("Descripcion"):
        #     if Maniobras == 'Maniobras de descarga' or Maniobras == 'Maniobras de carga':
        #         AddManiobras = {}
        #         AddManiobras["IDEvidencia"] = IDViaje
        #         AddManiobras[]
        #         ListEvidencias.append(Maniobras)
        return JsonResponse({'Evidencias': ListEvidencias})
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

def EvidenciasToList(Evidencia):
    ListEvi= list()
    for NewEvidencia in Evidencia:
        Delivery = {}
        Delivery["XD_IDPedido"]
        Delivery["Delivery"] = NewEvidencia.Delivery
        ListEvi.append(Viaje)
    return ListEvi

def SaveAprobarEvidencia(request):
    jParams = json.loads(request.body.decode('utf-8'))
    if jParams['TipoEvidencia'] == 'Pedido':
        SaveEvidenciaxPedido = XD_EvidenciasxPedido.objects.get(IDEvidenciaxPedido = jParams['IDSaveEvidencia'])
        SaveEvidenciaxPedido.IsValidada = True
        SaveEvidenciaxPedido.save()
    return HttpResponse("")    

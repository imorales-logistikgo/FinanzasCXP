from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from XD_Viajes.models import XD_Viajes, XD_PedidosxViajes, XD_Pedidos, XD_AccesoriosxViajes

def EvidenciasProveedor(request):
    SinEvidenciaDigital = XD_Viajes.objects.filter(IsEvidencia = False).count()
    SinEvidenciaFisica = XD_Viajes.objects.filter(IsEvidenciaFisica = False).count()
    return render(request, 'EvidenciasProveedor.html', {'EvidenciaDigital': SinEvidenciaDigital, 'EvidenciaFisica': SinEvidenciaFisica})

def FindFolioProveedor(request):
    Folio = request.GET["Folio"]
    arrFoliosEvidencias = list()
    try:
        XDFolio = XD_Viajes.objects.exclude(Status = 'CANCELADO').get(Folio = Folio, IsEvidenciaPedidos = 0, IsEvidenciaFisica = 0)
        GetDelivery = XD_PedidosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje).values_list("XD_IDPedido", flat=True)
        if GetDelivery:
            for Delivery in GetDelivery:
                newDelivery = {}
                a = XD_Pedidos.objects.get(XD_IDPedido = Delivery)
                newDelivery['XD_IDPedido'] = a.XD_IDPedido
                newDelivery['Delivery'] = a.Delivery
                arrFoliosEvidencias.append(newDelivery)
        else:
            arrFoliosEvidencias.append(XDFolio.Folio)
        for Maniobras in XD_AccesoriosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje).values_list("Descripcion", flat=True):
            if Maniobras == 'Maniobras de descarga' or Maniobras == 'Maniobras de carga':
                arrFoliosEvidencias.append(Maniobras)
        return JsonResponse({'Found': True, 'Folios': arrFoliosEvidencias})
    except Exception as e:
        print(e)
        return JsonResponse({'Found': False})

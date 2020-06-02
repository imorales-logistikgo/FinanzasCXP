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
        XDFolio = XD_Viajes.objects.get(Folio = Folio)
        GetDelivery = XD_PedidosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje).values_list("XD_IDPedido", flat=True)
        if GetDelivery:
            for Delivery in GetDelivery:
                a = XD_Pedidos.objects.get(XD_IDPedido = Delivery)
                arrFoliosEvidencias.append(a.Delivery)
        for Maniobras in XD_AccesoriosxViajes.objects.filter(XD_IDViaje = XDFolio.XD_IDViaje).values_list("Descripcion", flat=True):
            if Maniobras == 'Maniobras de descarga' or Maniobras == 'Maniobras de carga':
                arrFoliosEvidencias.append(Maniobras)
        return JsonResponse({'Found': True, 'Folios': arrFoliosEvidencias})
    except Exception as e:
        return JsonResponse({'Found': False})

def ListFolios (Folios):
    ListaFolios = list()
    for Folio in Folios:
        NuevFolio = {}
        NuevFolio["XD_IDPedido"] = Folio.XD_IDPedido
        ListaFolios.append(NuevFolio)
    return ListaFolios

import datetime
import json
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connections
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from XD_Viajes.models import XD_Viajes
from bkg_viajes.models import Bro_Viajes
from usersadmon.models import Cliente


@login_required

def ReporteGeneral(request):
    data= list()
    TipoViaje = Bro_Viajes.objects.exclude(Tipo=None).values('Tipo').distinct()
    Years = list()
    for i in range(-2, 5):
        Years.append(datetime.datetime.now().year + i)
    Status = XD_Viajes.objects.values('Status').distinct()
    Clientes = Cliente.objects.filter(isFiscal=True).exclude(Q(NombreCorto="") | Q(StatusProceso="BAJA"))
    return render(request, 'ReporteGeneral.html',
                  {'Years': Years, "page_obj": data, "Status": Status, 'Clientes': Clientes, 'Tipos': TipoViaje})

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def ReporteByFilter(request):
    FechaDesde = request.GET["FechaDescargaDesde"]
    FechaHasta = request.GET["FechaDescargaHasta"]
    Status = str(request.GET["Status"])[1:-1]
    Clientes =str(request.GET["Cliente"])[1:-1]
    TipoViaje = request.GET["TipoViaje"]
    with connections['users'].cursor() as cursor:
        cursor.execute('EXEC dbo.Op_XD_Bro_Viajes @Operacion=%s, @FechaDesde=%s, @FechaHasta=%s, @StatusProceso=%s,'
                           '@NombreComercialCliente=%s, @TipoViaje=%s',
                       [4, FechaDesde, FechaHasta, Status, Clientes, TipoViaje])
        Getdata = dictfetchall(cursor)
        # page = request.GET.get('page')
        # paginator = Paginator(Getdata, 500)
        # try:
        #     data = paginator.page(page)
        # except PageNotAnInteger:
        #     data = paginator.page(1)
        # except EmptyPage:
        #     data = paginator.page(paginator.num_pages)
    htmlRes = render_to_string('TablaReporteGeneral.html', {'page_obj': Getdata}, request=request,)
    return JsonResponse({'htmlRes':htmlRes})

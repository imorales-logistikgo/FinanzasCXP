import json
import time
import uuid
import calendar
from io import BytesIO

import schedule
from azure.storage.blob import BlobClient
from django.db import transaction
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
import datetime

from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from CartaNoAdeudo.models import CartaNoAdeudoTransportistas
from CartaNoAdeudo import views
from usersadmon.models import Proveedor


def CartaNoAdeudoMC(request):
    if request.user.roles == "Proveedor":
        FechaDescargaCarta = Proveedor.objects.get(IDTransportista=request.user.IDTransportista)
        CartasByProveedor = CartaNoAdeudoTransportistas.objects.filter(IDTransportista=request.user.IDTransportista,
                                                                       Tipo='MesaControl')
        if FechaDescargaCarta.FechaDescargaCartaNoAdeudoMC is not None:
            IsDescargaCartaNoAdeudo = True if FechaDescargaCarta.FechaDescargaCartaNoAdeudoMC.month - 1 == datetime.datetime.now().month - 1 else False
        else:
            IsDescargaCartaNoAdeudo = False
        return render(request, 'CartaNoAdeudoMC.html',
                      {"IsDescargaCartaNoAdeudo": IsDescargaCartaNoAdeudo, "CartasByProveedor": CartasByProveedor})
    elif request.user.roles == "MesaControl" or request.user.is_superuser:
        CartaNoAdeudoByProveedor = CartaNoAdeudoTransportistas.objects.filter(Tipo='MesaControl')
        return render(request, 'CartaNoAdeudoMC.html', {"CartaNoAdeudoByProveedor": CartaNoAdeudoByProveedor, "TipoCarta":"MesaControl"})
    elif request.user.roles == "users" or "CXP":
        return HttpResponse(status=403)
    else:
        raise Http404()


def CreateCartaNoadeudoMC(request):
    try:
        FechaDescargaCarta = Proveedor.objects.get(IDTransportista=request.user.IDTransportista)
        if FechaDescargaCarta.FechaDescargaCartaNoAdeudoMC is not None and FechaDescargaCarta.FechaDescargaCartaNoAdeudoMC.month - 1 == datetime.datetime.now().month - 1:
            resp = '<h2>Solo se puede descargar la carta una sola vez</h2>'
            return HttpResponse(resp)
        else:
            with transaction.atomic(using='users'):
                # FechaDescargaC = Proveedor.objects.get(IDTransportista=request.user.IDTransportista)
                # FechaDescargaCarta.FechaDescargaCartaNoAdeudoMC = datetime.datetime.now()
                # FechaDescargaCarta.save()
                w, h = A4
                date = datetime.datetime.now()
                months = (
                    "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
                    "Noviembre",
                    "Diciembre")
                day = date.day
                NombreProveedor = Proveedor.objects.get(IDTransportista=request.user.IDTransportista)
                month = months[date.month - 1]
                year = date.year
                messsage = "{} de {} del {}".format(day, month, year)
                bufferMemoria = BytesIO()
                c = canvas.Canvas(bufferMemoria, pagesize=A4)
                c.setTitle("CartaNoAdeudo-HojaLiberación.pdf")
                p = ParagraphStyle('test')
                p.alignment = TA_JUSTIFY
                p.fontSize = 13
                p.leading = 20
                p1 = ParagraphStyle('test')
                p1.alignment = TA_CENTER
                p1.fontSize = 13
                p1.leading = 15
                # local
                c.drawImage('static/img/F.png', -1, 5, 600, 841)
                # Demo
                # c.drawImage('C:\inetpub\Proyects\WebApps\LogistikGO-Finanzas-Demo\CuentasxPagar\static\img\F.png', -1, 5, 600, 841)
                # produccion
                # c.drawImage('C:\inetpub\Proyects\WebApps\LogistikGO-Finanzas\CuentasxPagar\static\img\F.png', -1, 5, 600, 841)
                # c.setFont("Helvetica-Bold",8)
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
                        date.month - GetMonth(request)] + " del " + str(year) + ".", p)
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
        transaction.rollback(using='users')
        return HttpResponse(status=500)


def upload(request):
    try:
        if 21 <= datetime.datetime.now().day <= \
                calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]:
            GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
                IDTransportista=request.user.IDTransportista,
                Status__in=('PENDIENTE', 'APROBADA'),
                MesCartaNoAdeudo=views.MesCartaNoAdeudo(
                    datetime.datetime.now(), 1), Tipo="MesaControl").exists()
        elif 1 <= datetime.datetime.now().day <= 5:
            GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
                IDTransportista=request.user.IDTransportista, Status__in=('PENDIENTE', 'APROBADA'),
                MesCartaNoAdeudo=views.MesCartaNoAdeudo(datetime.datetime.now(), 2, Tipo='MesaControl')).exists()
        elif 6 <= datetime.datetime.now().day <= 20:
            GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
                IDTransportista=request.user.IDTransportista, Status__in=('PENDIENTE', 'APROBADA'),
                MesCartaNoAdeudo=views.MesCartaNoAdeudo(datetime.datetime.now(), 2), Tipo='MesaControl').exists()
        if GetLastCartaUpload:
            return HttpResponse(status=500)
        else:
            if request.POST['type'] == 'application/pdf':
                namefile = str(uuid.uuid4()) + ".pdf"
            container_client = "evidencias"
            blob_service_client = BlobClient.from_connection_string(
                conn_str="DefaultEndpointsProtocol=http;AccountName=lgklataforma;AccountKey=SpHagQjk7C4dBPv1cse9w36zmAtweXIMjcw9DWve7ipgXgf2Fa5l+vw2k57EM8uinlUOkfxt34BQpC9FBHE+Yg==",
                container_name=container_client, blob_name=namefile)
            blob_service_client.upload_blob(request.FILES['files[]'])
            urlFile = blob_service_client.url
            return JsonResponse({"url": urlFile})
    except Exception as e:
        print(e)
        return HttpResponse(status=500)


def SaveCartaNoAdeudo(request,params):
    jParams = params
    try:
        if 21 <= datetime.datetime.now().day <= \
                calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]:
            GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
                IDTransportista=request.user.IDTransportista,
                Status__in=('PENDIENTE', 'APROBADA'),
                MesCartaNoAdeudo=views.MesCartaNoAdeudo(
                    datetime.datetime.now(), 1), Tipo=jParams["Tipo"]).exists()
            SaveMonth = True
        elif 1 <= datetime.datetime.now().day <= 5:
            GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
                IDTransportista=request.user.IDTransportista, Status__in=('PENDIENTE', 'APROBADA'),
                MesCartaNoAdeudo=views.MesCartaNoAdeudo(datetime.datetime.now(), 2), Tipo=jParams["Tipo"]).exists()
            SaveMonth = True
        elif 6 <= datetime.datetime.now().day <= 20:
            GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
                IDTransportista=request.user.IDTransportista, Status__in=('PENDIENTE', 'APROBADA'),
                MesCartaNoAdeudo=views.MesCartaNoAdeudo(datetime.datetime.now(), 2), Tipo=jParams["Tipo"]).exists()
            SaveMonth = False
        if GetLastCartaUpload:
            Response = 500
            return Response
        else:
            with transaction.atomic(using='users'):
                SaveCarta = CartaNoAdeudoTransportistas()
                SaveCarta.IDTransportista = Proveedor.objects.get(IDTransportista=request.user.IDTransportista)
                SaveCarta.IDUsuarioAlta = request.user.idusuario
                SaveCarta.FechaAlta = datetime.datetime.now()
                if SaveMonth:
                    SaveCarta.MesCartaNoAdeudo = views.MesCartaNoAdeudo(datetime.datetime.now(), 1)
                else:
                    SaveCarta.MesCartaNoAdeudo = views.MesCartaNoAdeudo(datetime.datetime.now(), 2)
                SaveCarta.RutaCartaNoAdeudo = jParams["RutaCartaNoAdeudo"]
                SaveCarta.Status = 'PENDIENTE'
                SaveCarta.Tipo = jParams["Tipo"]
                SaveCarta.save()
                Response = 200
                return Response
    except Exception as e:
        print(e)
        transaction.rollback(using='users')
        Response = 500
        return Response


def bloquearTransportistasByViaje(request):
    if 21 <= datetime.datetime.now().day <= \
            calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]:
        GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
            IDTransportista=request.user.IDTransportista,
            Status='APROBADA',
            MesCartaNoAdeudo=views.MesCartaNoAdeudo(
                datetime.datetime.now(), 1), Tipo="MesaControl").exists()
    elif 1 <= datetime.datetime.now().day <= 5:
        GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
            IDTransportista=request.user.IDTransportista, Status='APROBADA',
            MesCartaNoAdeudo=views.MesCartaNoAdeudo(datetime.datetime.now(), 2, Tipo='MesaControl')).exists()
    elif 6 <= datetime.datetime.now().day <= 20:
        GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
            IDTransportista=request.user.IDTransportista, Status='APROBADA',
            MesCartaNoAdeudo=views.MesCartaNoAdeudo(datetime.datetime.now(), 2), Tipo='MesaControl').exists()
    try:
        with transaction.atomic(using='users'):
            Transportista = Proveedor.objects.get(IDTransportista=request.user.IDTransportista)
            if not GetLastCartaUpload:
                Transportista.StatusProceso = 'BAJA'
                Transportista.save()
            else:
                Transportista.StatusProceso = 'VALIDADO'
                Transportista.save()
            transaction.commit(using='users')
    except Exception as e:
        transaction.rollback(using='users')
        print(e)


def GetMonth(request):
    NumberMonth = 1 if 21 <= datetime.datetime.now().day <= \
                       calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[
                           1] else 2 if 1 <= datetime.datetime.now().day <= 5 or 6 <= datetime.datetime.now().day <= 20 else 1
    print(NumberMonth)
    return NumberMonth



#def job():
 #   print("hello world")

# schedule.every(10).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every(5).to(10).minutes.do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
#schedule.every().minute.at(":17").do(job)

#while True:
 #   schedule.run_pending()
    # time.sleep(60)
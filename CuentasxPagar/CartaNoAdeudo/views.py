import os
import uuid
from django.shortcuts import render, redirect
from django.http import response, HttpResponse, Http404, JsonResponse
from io import BytesIO
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import json, datetime
from requests import Response
from usersadmon.models import Proveedor
from CartaNoAdeudo.models import CartaNoAdeudoTransportistas
from django.db import transaction
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient




def CartaNoAdeudo(request):
    if request.user.roles == "Proveedor":
        FechaDescargaCarta = Proveedor.objects.get(IDTransportista=request.user.IDTransportista)
        CartasByProveedor = CartaNoAdeudoTransportistas.objects.filter(IDTransportista=request.user.IDTransportista)
        if FechaDescargaCarta.FechaDescargaCartaNoAdeudo is not None:
            IsDescargaCartaNoAdeudo = True if FechaDescargaCarta.FechaDescargaCartaNoAdeudo.month -1 == datetime.datetime.now().month -1 else False
        else:
            IsDescargaCartaNoAdeudo = False
        return render(request, 'CartaNoAdeudo.html',{"IsDescargaCartaNoAdeudo":IsDescargaCartaNoAdeudo, "CartasByProveedor":CartasByProveedor})
    elif request.user.roles == "users":
        CartaNoAdeudoByProveedor = CartaNoAdeudoTransportistas.objects.filter()
        return render(request, 'CartaNoAdeudo.html', {"CartaNoAdeudoByProveedor": CartaNoAdeudoByProveedor})
    else:
        raise Http404()

def GetCartaNoAdeudo(request):
    try:
        FechaDescargaCarta = Proveedor.objects.get(IDTransportista = request.user.IDTransportista)
        if FechaDescargaCarta.FechaDescargaCartaNoAdeudo is not None and FechaDescargaCarta.FechaDescargaCartaNoAdeudo.month -1 == datetime.datetime.now().month -1:
            resp = '<h2>Solo se puede descargar la carta una sola vez</h2>'
            return HttpResponse(resp)
        else:
            with transaction.atomic(using='users'):
                FechaDescargaC = Proveedor.objects.get(IDTransportista=request.user.IDTransportista)
                FechaDescargaC.FechaDescargaCartaNoAdeudo = datetime.datetime.now()
                FechaDescargaC.save()
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
                para = Paragraph(
                    "Por medio de la presente me dirijo a usted para informar que no existen pendientes de facturar y/o cobrar "
                    "por parte de " + NombreProveedor.RazonSocial + " anteriores a " + months[
                        date.month - 2] + " " + str(year) + ", quedando pendiente por conciliar el periodo " + months[
                        date.month - 1] + "-" + months[12 - 1] + " " + str(year) + ", para concluir "
                    "satisfactoriamente y cerrar el ejercicio " + str(
                        year) + ".", p)
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



def SaveCartaNoAdeudo(request):
    try:
        jParams = json.loads(request.body.decode('utf-8'))
        GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(IDTransportista = request.user.IDTransportista).exclude(Status='RECHAZADA').last()
        if GetLastCartaUpload.MesCartaNoAdeudo == MesCartaNoAdeudo(datetime.datetime.now()) if GetLastCartaUpload is not None else False:
            return HttpResponse(status=500)
        else:
            with transaction.atomic(using='users'):
                SaveCarta = CartaNoAdeudoTransportistas()
                SaveCarta.IDTransportista = Proveedor.objects.get(IDTransportista = request.user.IDTransportista)
                SaveCarta.IDUsuarioAlta = request.user.idusuario
                SaveCarta.FechaAlta = datetime.datetime.now()
                SaveCarta.MesCartaNoAdeudo = MesCartaNoAdeudo(datetime.datetime.now())
                SaveCarta.RutaCartaNoAdeudo = jParams["RutaCartaNoAdeudo"]
                SaveCarta.Status = 'PENDIENTE'
                SaveCarta.save()
                return HttpResponse(status=200)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

def MesCartaNoAdeudo(Fecha):
    months = (
        "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
        "Noviembre",
        "Diciembre")
    MesCarta = months[Fecha.month - 2]
    print(MesCarta)
    return MesCarta

def AprobarCarta(request):
    try:
        jParams = json.loads(request.body.decode('utf-8'))
        with transaction.atomic(using='users'):
            CartaAprobar = CartaNoAdeudoTransportistas.objects.get(IDCartaNoAdeudo = jParams["IDCarta"])
            CartaAprobar.Status = "APROBADA"
            CartaAprobar.IDUsuarioAprueba = request.user.idusuario
            CartaAprobar.FechaAprueba = datetime.datetime.now()
            CartaAprobar.save()
            return HttpResponse(status=200)
    except Exception as e:
        print(e)
        transaction.rollback(using='users')
        return HttpResponse(status=500)

def RechazarCarta(request):
    try:
        jParams = json.loads(request.body.decode('utf-8'))
        with transaction.atomic(using='users'):
            CartaRechazar = CartaNoAdeudoTransportistas.objects.get(IDCartaNoAdeudo = jParams["IDCarta"])
            CartaRechazar.Status = 'RECHAZADA'
            CartaRechazar.IDUsuarioRechaza = request.user.idusuario
            CartaRechazar.FechaRechaza = datetime.datetime.now()
            CartaRechazar.ComentarioRechazo = jParams["ComentarioRechazo"]
            CartaRechazar.save()
            return HttpResponse(status=200)
    except Exception as e:
        print(e)
        transaction.rollback(using='users')
        return HttpResponse(status=500)

def upload(request):
    try:
        GetLastCartaUpload = CartaNoAdeudoTransportistas.objects.filter(
            IDTransportista=request.user.IDTransportista).exclude(Status='RECHAZADA').last()
        if GetLastCartaUpload.MesCartaNoAdeudo == MesCartaNoAdeudo(datetime.datetime.now()) if GetLastCartaUpload is not None else False:
            return HttpResponse(status=500)
        else:
            print("si entro")
            if request.POST['type'] == 'application/pdf':
                namefile = str(uuid.uuid4()) + ".pdf"
            container_client = "evidencias"
            blob_service_client = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=http;AccountName=lgklataforma;AccountKey=SpHagQjk7C4dBPv1cse9w36zmAtweXIMjcw9DWve7ipgXgf2Fa5l+vw2k57EM8uinlUOkfxt34BQpC9FBHE+Yg==",container_name=container_client, blob_name=namefile)
            blob_service_client.upload_blob(request.FILES['files[]'])
            urlFile = blob_service_client.url
            return JsonResponse({"url":urlFile})
    except Exception as e:
        print(e)
        return HttpResponse(status=500)


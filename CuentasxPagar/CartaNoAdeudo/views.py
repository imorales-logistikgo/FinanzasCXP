from django.shortcuts import render
from django.http import response, HttpResponse
from io import BytesIO
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import json, datetime
from usersadmon.models import Proveedor

def CartaNoAdeudo(request):
    return render(request, 'CartaNoAdeudo.html')

def GetCartaNoAdeudo(request):
    w, h = A4
    date = datetime.datetime.now()
    months = (
        "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre",
        "Diciembre")
    day = date.day
    NombreProveedor = Proveedor.objects.get(IDTransportista = request.user.IDTransportista)
    month = months[date.month - 1]
    year = date.year
    messsage = "{} de {} del {}".format(day, month, year)
    bufferMemoria = BytesIO()
    c = canvas.Canvas(bufferMemoria, pagesize=A4)
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
        "por parte de "+NombreProveedor.RazonSocial+" anteriores a "+months[date.month - 2] +" "+ str(year)+", quedando pendiente por conciliar el periodo "+months[date.month - 1]+"-"+months[12 - 1]+" "+str(year)+", para conciliar "
        "satisfactoriamente y cerrar el ejercicio "+str(year)+".", p)
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
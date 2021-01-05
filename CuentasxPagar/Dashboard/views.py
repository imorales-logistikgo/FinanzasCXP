import json
import socket
import random
from time import strftime

from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import requests
from users import models as User
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import datetime
from django.contrib.auth.decorators import login_required
from usersadmon.models import AdmonUsuarios, Proveedor, AdmonCorreosxTransportista
from .forms import FormCreateUser, FormEliminarEvidencias
from bkg_viajes.models import Bro_Viajes, Bro_EvidenciasxViaje
from XD_Viajes.models import XD_Viajes, XD_EvidenciasxPedido, XD_EvidenciasxViaje, XD_PedidosxViajes
from django.conf import settings
from io import BytesIO
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import calendar
from PendientesEnviar import views

@login_required
def Dashboard(request):
    if request.user.username == 'cxp1@logistikgo' or request.user.is_superuser:
        form = FormCreateUser()
        GetProveedores = User.User.objects.filter(roles='Proveedor').values('id', 'name', 'is_active', 'last_login',
                                                                            'idusuario')
        for each in GetProveedores:
            GetProv = AdmonUsuarios.objects.get(idusuario=each["idusuario"])
            each["FechaActualizacion"] = GetProv.fechacambiocontrasena
            each["FechaProximaUpdate"] = GetProv.fechacambiocontrasena + relativedelta(
                months=2) if GetProv.fechacambiocontrasena != None else None
        # SearchEvidencia = FormEliminarEvidencias()
        Proveedores = Proveedor.objects.filter().values('IDTransportista','RazonSocial')
        for each in Proveedores:
            if AdmonCorreosxTransportista.objects.filter(IDTransportista=each["IDTransportista"]).exists():
                datos = AdmonCorreosxTransportista.objects.filter(IDTransportista=each["IDTransportista"]).first()
                each["Correo"] = datos.Correo
            else:
                each["Correo"] = None
        return render(request, 'Dashboard.html',
                      {'form': form, 'ActiveUpdatePassword': 'active',
                       'GetProveedores':GetProveedores, 'Proveedores': Proveedores})
    elif request.user.username == 'wbarrones@logistikgo':
        Proveedores = Proveedor.objects.filter().values('IDTransportista', 'RazonSocial')
        return render(request, 'Dashboard.html', {'Proveedores': Proveedores, 'ActiveAddCorreoTransportista': 'active'})
    else:
        return redirect('/Usuario/logout')


def ManualPDF(request):
    with open(settings.MANUAL_CXP, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=Manual_cxp_proveedores.pdf'
        return response
    pdf.closed


def AltaUsuarioProveedor(request):
    if request.method == 'POST':
        form = FormCreateUser(request.POST)
        if form.is_valid():
            RFC = form.cleaned_data.get('RFC')
            RFCToUPPER = RFC.upper()
            if Proveedor.objects.filter(RFC=RFCToUPPER).exists():
                UserProv = AdmonUsuarios.objects.filter(nombreusuario=RFCToUPPER).exists()
                if not UserProv:
                    result = SaveUserProveedor(RFCToUPPER)
                    Msj = 'Usuario creado exitosamente' if result == 201 else "Ocurrio un error"
                    return render(request, 'Dashboard.html',
                                  {'form': FormCreateUser(), 'SearchEvidencia': FormEliminarEvidencias(),
                                   'success' if result == 201 else 'error': Msj, 'ActiveCrearProveedor': 'active'})

                else:
                    result = SaveUserDjango(RFCToUPPER)
                    Msj = 'Usuario creado exitosamente' if result == 201 else "El usuario ya esta registrado" if result == 200 else "Ocurrio un error"
                    return render(request, 'Dashboard.html',
                                  {'form': FormCreateUser(), 'SearchEvidencia': FormEliminarEvidencias(),
                                   'success' if result == 201 else 'warning' if result == 200 else 'error': Msj,
                                   'ActiveCrearProveedor': 'active'})
            else:
                err = "Proveedor no encontrado, por favor intenta con otro RFC"
                return render(request, 'Dashboard.html',
                              {'form': FormCreateUser(), 'SearchEvidencia': FormEliminarEvidencias(), 'error': err,
                               'ActiveCrearProveedor': 'active'})
        else:
            err = "Datos invalidos, por favor inserta los datos correctos."
            return render(request, 'Dashboard.html',
                          {'form': FormCreateUser(), 'SearchEvidencia': FormEliminarEvidencias(), 'error': err,
                           'ActiveCrearProveedor': 'active'})
    return redirect('Dashboard')


def SaveUserProveedor(rfc):
    try:
        with transaction.atomic(using='users'):
            GetDatosProveedor = Proveedor.objects.get(RFC=rfc)
            newUser = AdmonUsuarios()
            newUser.nombre = GetDatosProveedor.RazonSocial
            newUser.nombreusuario = GetDatosProveedor.RFC
            newUser.correo = GetDatosProveedor.Correo
            newUser.fechacambiocontrasena = datetime.datetime.now()
            newUser.hasbytes = 0
            newUser.saltbytes = 0
            newUser.periodo = 365
            newUser.statusreg = "ACTIVO"
            newUser.apepaterno = ""
            newUser.apematerno = ""
            newUser.save()
            DjangoUser = User.User.objects.filter(
                IDTransportista=GetDatosProveedor.IDTransportista).exists()
            if not DjangoUser:
                print("here")
                user = User.User()
                user.name = newUser.nombre + " " + newUser.apepaterno + " " + newUser.apematerno
                user.email = newUser.correo
                user.idusuario = newUser.idusuario
                user.is_staff = False
                user.roles = "Proveedor"
                user.IDTransportista = GetDatosProveedor.IDTransportista
                print("here2")
                user.save()
            return 201
    except Exception as e:
        print(e)
        transaction.rollback(using='users')
        return 500


def SaveUserDjango(rfc):
    GetDatosProveedor = Proveedor.objects.get(RFC=rfc)
    DjangoUser = User.User.objects.filter(
        IDTransportista=GetDatosProveedor.IDTransportista).exists()
    try:
        if not DjangoUser:
            GetUserFromAdmonUsuarios = AdmonUsuarios.objects.get(nombreusuario=rfc)
            with transaction.atomic(using='users'):
                user = User.User()
                user.name = GetUserFromAdmonUsuarios.nombre + " " + GetUserFromAdmonUsuarios.apepaterno + " " + GetUserFromAdmonUsuarios.apematerno
                user.email = GetUserFromAdmonUsuarios.correo
                user.idusuario = GetUserFromAdmonUsuarios.idusuario
                user.is_active = False
                user.is_staff = False
                user.roles = "Proveedor"
                user.IDTransportista = GetDatosProveedor.IDTransportista
                user.save()
                transaction.commit(using='users')
                return 201
        else:
            return 200
    except Exception as e:
        print(e)
        transaction.rollback(using='users')
        return 500


def GetEvidenciasByFolio(request):
    Folio = request.GET.get('Viaje')
    if Folio[:3] == "FTL":
        try:
            ListaEvidencias = list()
            GetEvidenciaBKG = Bro_Viajes.objects.get(Folio=Folio)
            EvidenciasBKG = Bro_EvidenciasxViaje.objects.filter(IDBro_Viaje=GetEvidenciaBKG.IDBro_Viaje)
            for EachEvidencia in EvidenciasBKG:
                Evidencia = {}
                Evidencia["Titulo"] = EachEvidencia.Titulo
                ListaEvidencias.append(Evidencia)
            print(ListaEvidencias)
            return render(request, 'Dashboard.html',
                          {'SearchEvidencia': FormEliminarEvidencias(), 'form': FormCreateUser(),
                           'ActiveEvidencias': 'active', 'Folio': GetEvidenciaBKG.Folio,
                           'AllEvidencias': ListaEvidencias})
        except:
            return render(request, 'Dashboard.html',
                          {'SearchEvidencia': FormEliminarEvidencias(), 'form': FormCreateUser(),
                           'ErrorEvidencia': 'Folio no encontrado, por favor intenta con otro folio',
                           'ActiveEvidencias': 'active'})

    elif Folio[:3] == "XDD":
        GetEvidenciasXD = XD_Viajes.objects.get(Folio=Folio)
    else:
        return render(request, 'Dashboard.html', {'SearchEvidencia': FormEliminarEvidencias(), 'form': FormCreateUser(),
                                                  'ErrorEvidencia': 'Folio no encontrado, por favor intenta con otro folio',
                                                  'ActiveEvidencias': 'active'})


def UpdatePassword(IDUsuario=None):
    GetProveedores = User.User.objects.filter(roles='Proveedor', is_active=1) if IDUsuario is None else User.User.objects.filter(idusuario=IDUsuario)
    for i in GetProveedores:
        GetLastFechaUpdate = AdmonUsuarios.objects.get(idusuario=i.idusuario)
        if GetLastFechaUpdate.fechacambiocontrasena >= GetLastFechaUpdate.fechacambiocontrasena+relativedelta(months=2):
            password = GeneradorPassword(i.IDTransportista)
            jsonParams = {'strPassword': password, 'IDUsuario': i.idusuario}
            respose = requests.post(settings.API_ADMON + "api/Usuarios/ActualizarContrasenaProveedor",
                                    headers={'content-type': 'application/json'}, json=jsonParams)
            if respose.status_code == 201:
                EnviarCorreoContraseñaProveedor(i.IDTransportista, password)
    return "ok"


def GeneradorPassword(IDTransportista):
    IDTransportista = IDTransportista
    CaracterEspecial = "".join(random.sample(".*#$%", 1))
    PasswordDefault = 'Lgk' + CaracterEspecial + str(IDTransportista)
    Caracteres = "abcdefghijklmnopqrstuvwxyz.*#$%0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    PasswordRadom = "".join(random.sample(Caracteres, 5))
    PasswordNueva = PasswordDefault + PasswordRadom
    return PasswordNueva


def EnviarCorreoContraseñaProveedor(IDTransportista, password):
    print("yes")
    # GetIDUsuarioProveedor = User.User.objects.get(IDTransportista=IDTransportista)
    # try:
    #     CorreoProveedor = list(
    #         AdmonCorreosxTransportista.objects.filter(IDTransportista=GetIDUsuarioProveedor.IDTransportista,
    #                                                   IsEnviarCorreo=1).values('Correo'))
    #     if CorreoProveedor != []:
    #         SendEmail = list()
    #         for new in CorreoProveedor:
    #             SendEmail.append(new["Correo"], )
    #         RS = Proveedor.objects.get(IDTransportista=GetIDUsuarioProveedor.IDTransportista)
    #         context = {
    #             'nombre': RS.RazonSocial,
    #             'user': GetIDUsuarioProveedor.username,
    #             'password': password,
    #         }
    #         html_content = render_to_string("CorreoContrasenaProveedor.html", context)
    #         subject = 'Cambio de Contraseña'
    #         from_email = settings.EMAIL_HOST_USER
    #         to = SendEmail
    #         bcc = ['jfraga@logisti-k.com.mx', 'jcastillo@logisti-k.com.mx', 'ugaytan@logisti-k.com.mx']
    #         msg = EmailMessage(subject, html_content, from_email, to, bcc=bcc)
    #         msg.content_subtype = "html"
    #         msg.send()
    #         return "Success"
    #     else:
    #         return "Error"
    # except Exception as e:
    #     print(e)
    #     return "Error"


def GetIPAdress(salf):
    hostname = socket.gethostname()
    IPAdress = socket.gethostbyname(hostname)
    print(IPAdress)


def BloquearAccesoProveedor(request):
    try:
        with transaction.atomic(using='default'):
            jParams = json.loads(request.body.decode('utf-8'))
            GetUsuario = User.User.objects.get(id=jParams["IDUsuario"])
            GetUsuario.is_active = False
            GetUsuario.save()
            return HttpResponse(status=200)
    except Exception as e:
        transaction.rollback(using='default')
        print(e)
        return HttpResponse(status=500)


def DesbloquearAccesoProveedor(request):
    try:
        with transaction.atomic(using='default'):
            print("here")
            jParams = json.loads(request.body.decode('utf-8'))
            print(jParams)
            print("gere")
            GetUsuario = User.User.objects.get(id=jParams["IDUsuario"])
            GetUsuario.is_active = True
            GetUsuario.save()
            # if request.user.username == 'cxp3@logistikgo':
            #     UpdatePassword(jParams["IDUsuario"])
            return HttpResponse(status=200)
    except Exception as e:
        transaction.rollback(using='default')
        print(e)
        return HttpResponse(status=500)


def GetDetallesCorreo(request):
    IDTransportista = request.GET.get('IDTransportista')
    try:
        GetData = AdmonCorreosxTransportista.objects.filter(IDTransportista=IDTransportista)
        htmlRes = render_to_string('TablaDetalleCorreos.html', {'Correos': GetData}, request=request, )
        return JsonResponse({'htmlRes': htmlRes})
    except Exception as e:
        print(e)
        return HttpResponse(status=500)

def AddCorreoByTransportista(request):
    try:
        with transaction.atomic(using='users'):
            jParams = json.loads(request.body.decode('utf-8'))
            if "@" in jParams["Correo"]:
                AddCorreo = AdmonCorreosxTransportista()
                AddCorreo.IDTransportista = Proveedor.objects.get(IDTransportista=jParams["IDTransportista"])
                AddCorreo.Correo = jParams["Correo"]
                AddCorreo.IsEnviarCorreo = True
                AddCorreo.save()
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=500)
    except Exception as e:
        print(e)
        transaction.rollback(using='users')
        return HttpResponse(status=500)

def ActivarOrDesactivarCorreoToSendEmail(request):
    try:
        with transaction.atomic(using='users'):
            jParams = json.loads(request.body.decode('utf-8'))
            ActivarCorreo = AdmonCorreosxTransportista.objects.get(IDCorreoxTransportista=jParams['IDCorreo'])
            ActivarCorreo.IsEnviarCorreo = True if jParams["Accion"] == 'ActivarCorreo' else False
            ActivarCorreo.save()
            return HttpResponse(status=200)
    except Exception as e:
        print(e)
        transaction.rollback(using='users')
        return HttpResponse(status=500)


def CreateCartaNoAdeudoCXP(IDTransportista):
    GetViajesThisMonth = views.GetTotalViajesEn1Mes(IDTransportista, 1)
    date = datetime.datetime.now()
    months = (
        "Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
        "Noviembre", "Diciembre")
    day = date.day
    NombreProveedor = Proveedor.objects.get(IDTransportista=IDTransportista)
    month = months[date.month - 1]
    year = date.year
    messsage = "{} de {} del {}".format(day, month, year)
    bufferMemoria = BytesIO()
    c = canvas.Canvas(bufferMemoria, pagesize=A4)
    c.setTitle("CartaNoAdeudo-PendienteFacturar.pdf")
    p = ParagraphStyle('test')
    p.alignment = TA_JUSTIFY
    p.fontSize = 13
    p.leading = 20
    p1 = ParagraphStyle('test')
    p1.alignment = TA_CENTER
    p1.fontSize = 13
    p1.leading = 15

    c.drawImage(settings.RUTA_IMG_PDF, -1, 5, 600, 841)
    c.drawString(300, 690, "San Luis Potosí, S.L.P. a " + str(messsage))
    c.drawString(100, 640, "Logisti-k de México SA de CV")
    c.drawString(100, 620, "Av. Chapultepec #1385 3er. Piso")
    c.drawString(100, 600, "Privadas del Pedregal, S.L.P.")
    c.drawString(100, 550, "ATENCION:")
    c.drawString(100, 520, "C.P. Judith Castillo Zavala")
    c.drawString(100, 500, "Gerente de Finanzas")
    para = Paragraph(
        "Por medio de la presente me dirijo a usted para informar que no existen pendientes de facturar y/o cobrar "
        "por parte de " + NombreProveedor.RazonSocial + " anteriores al " + str(
            calendar.monthrange(datetime.datetime.now().year,
                                datetime.datetime.now().month - 1 if GetViajesThisMonth else datetime.datetime.now().month - 2)[
                1]) + " " + months[
            date.month - 2 if GetViajesThisMonth else date.month - 3] + " " + str(
            year) + ", quedando pendiente por conciliar el periodo " + months[
            date.month - 1 if GetViajesThisMonth else date.month - 2] + "-" + months[12 - 1] + " " + str(
            year) + ", para concluir "
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
    return pdf
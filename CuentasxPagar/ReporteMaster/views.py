from django.shortcuts import render
from ReporteMaster.models import View_Master_Proveedor
from usersadmon.models import Proveedor, AdmonUsuarios
import json, datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

@login_required
def GetReporteMaster(request):
	if request.user.roles == 'Proveedor' or request.user.roles == 'Contabilidad':
		 return render(request, '404.html')
	else:
		ReporteMaster = View_Master_Proveedor.objects.all()#filter(FechaDescarga__month = datetime.datetime.now().month, FechaDescarga__year = datetime.datetime.now().year)
		Proveedores = Proveedor.objects.all()
		return render(request, 'Master.html', {'ReporteMaster': ReporteMaster, 'Proveedores': Proveedores})

def PEToList(Facturas):
	ListData = list()
	for Fact in Facturas:
		if Fact.StatusFacturaProveedor != 'DEPURADO':
			Reporte = {}
			Reporte["Folio"] = Fact.Folio
			Reporte["NombreCortoCliente"] = Fact.NombreCortoCliente
			Reporte["NombreCortoProveedor"] = Fact.NombreCortoProveedor
			Reporte["FechaDescarga"] = Fact.FechaDescarga
			Reporte["MonedaProveedor"] = Fact.MonedaProveedor
			Reporte["MonedaCliente"] = Fact.MonedaCliente
			Reporte["Status"] = Fact.Status
			Reporte["IsEvidenciaDigital"] = Fact.IsEvidenciaDigital
			Reporte["IsEvidenciaFisica"] = Fact.IsEvidenciaFisica
			Reporte["Proyecto"] = Fact.Proyecto
			Reporte["TipoConcepto"] = Fact.TipoConcepto
			Reporte["IsFacturaCliente"] = Fact.IsFacturaCliente
			Reporte["FolioFactCliente"] = Fact.FolioFactCliente
			Reporte["StatusFacturaCliente"] = Fact.StatusFacturaCliente
			Reporte["SubtotalFacturaCliente"] = Fact.SubtotalFacturaCliente
			Reporte["IvaFacturaCliente"] = Fact.IvaFacturaCliente
			Reporte["RetencionFactura"] = Fact.RetencionFactura
			Reporte["TotalFacturaCliente"] = Fact.SubtotalFacturaCliente
			Reporte["SubtotalC"] = Fact.SubtotalC
			Reporte["IVAC"] = Fact.IVAC
			Reporte["RetencionC"] = Fact.RetencionC
			Reporte["TotalC"] = Fact.TotalC
			Reporte["IsFacturaProveedor"] = Fact.IsFacturaProveedor
			Reporte["FolioFactProveedor"] = Fact.FolioFactProveedor
			Reporte["SubtotalFacturaProveedor"] = Fact.SubtotalFacturaProveedor
			Reporte["IvaFacturaProveedor"] = Fact.IvaFacturaProveedor
			Reporte["RetencionFacturaProveedor"] = Fact.RetencionFacturaProveedor
			Reporte["TotalFacturaProveedor"] = Fact.SubtotalFacturaProveedor
			Reporte["StatusFacturaProveedor"] = 'RECHAZADA' if(Fact.StatusFacturaProveedor == 'CANCELADA') else Fact.StatusFacturaProveedor
			Reporte["MOP"] = Fact.MOP
			Reporte["Subtotal"] = Fact.Subtotal
			Reporte["IVA"] = Fact.IVA
			Reporte["Retencion"] = Fact.Retencion
			Reporte["Total"] = Fact.Total
			Reporte["CostoSubtotalAnterior"] = Fact.CostoSubtotalAnterior
			Reporte["CostoIVAAnterior"] = Fact.CostoIVAAnterior
			Reporte["CostoRetencionAnterior"] = Fact.CostoRetencionAnterior
			Reporte["CostoTotalAnterior"] = Fact.CostoTotalAnterior
			Reporte["NuevoCosto"] = Fact.NuevoCosto
			Reporte["NuevoCostoAccesorios"] = Fact.NuevoCostoAccesorios
			Reporte["NuevoCostoRecoleccion"] = Fact.NuevoCostoRecoleccion
			Reporte["NuevoCostoRepartos"] = Fact.NuevoCostoRepartos
			Reporte["NuevoCostoSubtotal"] = Fact.NuevoCostoSubtotal
			Reporte["NuevoCostoIVA"] = Fact.NuevoCostoIVA
			Reporte["NuevoCostoRetencion"] = Fact.NuevoCostoRetencion
			Reporte["NuevoCostoTotal"] = Fact.NuevoCostoTotal
			ListData.append(Reporte)
	return ListData

def GetFacturasByFilters(request):
	Proveedores = json.loads(request.GET["Proveedor"])
	Moneda = json.loads(request.GET["Moneda"])
	Status = json.loads(request.GET["Status"])
	Proyectos = json.loads(request.GET["Proyecto"])
	if "Year" in request.GET:
		arrMonth = json.loads(request.GET["arrMonth"])
		Year = request.GET["Year"]
		Facturas = View_Master_Proveedor.objects.filter(FechaDescarga__month__in = arrMonth, FechaDescarga__year = Year)#.exclude(StatusFacturaProveedor = 'DEPURADO')
	else:
		Facturas = View_Master_Proveedor.objects.filter(FechaDescarga__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')])#.exclude(StatusFacturaProveedor = 'DEPURADO')
	if Proveedores:
		Facturas = Facturas.filter(NombreCortoProveedor__in = Proveedores)
	if Moneda:
		Facturas = Facturas.filter(MonedaProveedor__in=Moneda, MonedaCliente__in=Moneda)
	if Status:
		Facturas = Facturas.filter(Status__in = Status)#.exclude(StatusFacturaProveedor = 'DEPURADO')
	if Proyectos:
		Facturas = Facturas.filter(Proyecto__in = Proyectos)
	ListData = PEToList(Facturas)
	htmlRes = render_to_string('TablaReporteMaster.html', {'ReporteMaster':ListData}, request = request,)
	return JsonResponse({'htmlRes':htmlRes})



from django.shortcuts import render
from ReporteMaster.models import View_Master_Proveedor
from usersadmon.models import Proveedor, AdmonUsuarios
import json, datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

@login_required
def GetReporteMaster(request):
	if request.user.roles == 'Proveedor':
		 return render(request, '404.html')
	else:
		ReporteMaster = View_Master_Proveedor.objects.all()
		Proveedores = Proveedor.objects.all()
		return render(request, 'Master.html', {'ReporteMaster': ReporteMaster, 'Proveedores': Proveedores})

def PEToList(Facturas):
	ListData = list()
	for Fact in Facturas:
		Reporte = {}
		Reporte["Folio"] = Fact.Folio
		Reporte["NombreCortoCliente"] = Fact.NombreCortoCliente
		Reporte["NombreCortoProveedor"] = Fact.NombreCortoProveedor
		Reporte["FechaDescarga"] = Fact.FechaDescarga
		Reporte["Moneda"] = Fact.Moneda
		Reporte["Status"] = Fact.Status
		Reporte["IsEvidenciaDigital"] = Fact.IsEvidenciaDigital
		Reporte["IsEvidenciaFisica"] = Fact.IsEvidenciaFisica
		Reporte["Proyecto"] = Fact.Proyecto
		Reporte["TipoConcepto"] = Fact.TipoConcepto
		Reporte["IsFacturaCliente"] = Fact.IsFacturaCliente
		Reporte["FolioFactCliente"] = Fact.FolioFactCliente
		Reporte["CostoSubtotal"] = Fact.CostoSubtotal
		Reporte["CostoIVA"] = Fact.CostoIVA
		Reporte["CostoRetencion"] = Fact.CostoRetencion
		Reporte["CostoTotal"] = Fact.CostoTotal
		Reporte["IsFacturaProveedor"] = Fact.IsFacturaProveedor
		Reporte["FolioFactProveedor"] = Fact.FolioFactProveedor
		Reporte["MOP"] = Fact.MOP
		Reporte["PrecioSubtotal"] = Fact.PrecioSubtotal
		Reporte["PrecioIVA"] = Fact.PrecioIVA
		Reporte["PrecioRetencion"] = Fact.PrecioRetencion
		Reporte["PrecioTotal"] = Fact.PrecioTotal
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
		Facturas = View_Master_Proveedor.objects.filter(FechaDescarga__month__in = arrMonth, FechaDescarga__year = Year)
	else:
		Facturas = View_Master_Proveedor.objects.filter(FechaDescarga__range = [datetime.datetime.strptime(request.GET["FechaFacturaDesde"],'%m/%d/%Y'), datetime.datetime.strptime(request.GET["FechaFacturaHasta"],'%m/%d/%Y')])
	if Proveedores:
		Facturas = Facturas.filter(NombreCortoProveedor__in = Proveedores)
	if Moneda:
		Facturas = Facturas.filter(Moneda__in = Moneda)
	if Status:
		Facturas = Facturas.filter(Status__in = Status)
	if Proyectos:
		Facturas = Facturas.filter(Proyecto__in = Proyectos)
	ListData = PEToList(Facturas)
	htmlRes = render_to_string('TablaReporteMaster.html', {'ReporteMaster':ListData}, request = request,)
	print(htmlRes)
	return JsonResponse({'htmlRes' : htmlRes})

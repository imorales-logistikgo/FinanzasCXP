from django.shortcuts import render
from ReporteMaster.models import View_Master_Proveedor

def GetReporteMaster(request):
	ReporteMaster = View_Master_Proveedor.objects.all()
	return render(request, 'Master.html', {'ReporteMaster': ReporteMaster})

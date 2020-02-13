from django.shortcuts import render
from ReporteMaster.models import View_Master_Proveedor
def GetReporteMaster(request):
	Master = View_Master_Proveedor.objects.filter(Status__in = ["FINALIZADO", "COMPLETO", "ENTREGADO"])
	return render(request, 'Master.html', {'Master': Master})

from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
from django.contrib.auth.decorators import login_required
from PendientesEnviar.models import View_PendientesEnviarCxP
@login_required

def Indicadores(request):
	today = date.today()
	PE = View_PendientesEnviarCxP.objects.filter(FechaDescarga__year = today.year, FechaDescarga__month = today.month, FechaDescarga__day = today.day)
	print(PE)
	return render(request, 'Dashboard.html', {'today': today});


def ManualPDF(request):
    with open('static/pdf/Manual_cxp_proveedores.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=Manual_cxp_proveedores.pdf'
        return response
    pdf.closed
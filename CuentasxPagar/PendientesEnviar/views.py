from django.shortcuts import render
from django.http import HttpResponse


def PendienteEnviar(request):
	return render(request, 'PendientesEnviar.html')
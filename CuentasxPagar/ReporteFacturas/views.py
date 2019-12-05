from django.shortcuts import render
from django.http import HttpResponse


def ReporteFacturas(request):
	return render(request, 'ReporteFacturas.html')

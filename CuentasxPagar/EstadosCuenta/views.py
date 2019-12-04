from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def EstadosCuenta(request):
	return render(request, 'EstadosCuenta.html');

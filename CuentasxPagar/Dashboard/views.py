from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def Indicadores(request):
	return render(request, 'Dashboard.html');

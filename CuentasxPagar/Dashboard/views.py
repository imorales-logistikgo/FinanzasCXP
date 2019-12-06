from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
# Create your views here.

def Indicadores(request):
	today = date.today()
	return render(request, 'Dashboard.html', {'today': today});

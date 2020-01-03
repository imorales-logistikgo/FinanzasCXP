from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
from django.contrib.auth.decorators import login_required
@login_required

def Indicadores(request):
	today = date.today()
	return render(request, 'Dashboard.html', {'today': today});

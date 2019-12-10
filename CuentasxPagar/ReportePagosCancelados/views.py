from django.shortcuts import render

def ReportePagosCancelados(request):
    return render(request, 'PagosCancelados.html')

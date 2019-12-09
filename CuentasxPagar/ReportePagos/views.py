from django.shortcuts import render
from EstadosCuenta.models import RelacionPagosFacturasxProveedor, PagosxProveedor

def ReportePagos(request):
	Pagos = PagosxProveedor.objects.all()
	#for Pago in Pagos:
	return render(request, 'ReportePagos.html', {"Cobros": Pagos});

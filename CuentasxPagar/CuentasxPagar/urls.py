"""CuentasxPagar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('Dashboard/', include('Dashboard.urls')),
    path('', include('PendientesEnviar.urls')),
    path('PendientesEnviar/', include('PendientesEnviar.urls')),
    path('EstadosdeCuenta/', include('EstadosCuenta.urls')),
    path('ReporteFacturas/', include('ReporteFacturas.urls')),
    path('ReportePagos/', include('ReportePagos.urls')),
    path('ReporteCanceladas/', include('ReporteCanceladas.urls')),
    path('ReportePagosCancelados/', include('ReportePagosCancelados.urls')),
    path('ReporteMaster/', include('ReporteMaster.urls')),
    path('EvidenciasProveedor/', include('EvidenciasProveedor.urls')),
    path('Usuario/', include('users.urls')),
    path('CartaNoAdeudo/', include('CartaNoAdeudo.urls')),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += path('_debug_/', include(debug_toolbar.urls)),

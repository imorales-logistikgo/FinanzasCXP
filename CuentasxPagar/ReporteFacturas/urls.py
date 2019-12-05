from django.urls import path
from . import views

urlpatterns = [
    path('ReporteFacturas', views.ReporteFacturas, name='ReporteFacturas'),
]

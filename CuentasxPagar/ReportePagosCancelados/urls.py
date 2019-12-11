from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportePagosCancelados, name='ReportePagosCancelados'),
]

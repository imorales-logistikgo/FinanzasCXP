from django.urls import path
from . import views

urlpatterns = [
    path('PendienteEnviar', views.PendienteEnviar, name='PendienteEnviar'),
]
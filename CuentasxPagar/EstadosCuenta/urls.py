from django.urls import path
from . import views
urlpatterns = [
    path('EstadosCuenta', views.EstadosCuenta, name='EstadosCuenta'),
]

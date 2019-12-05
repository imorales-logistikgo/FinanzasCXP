from django.urls import path
from . import views
urlpatterns = [
    path('ReportePagos', views.ReportePagos, name='ReportePagos'),
]

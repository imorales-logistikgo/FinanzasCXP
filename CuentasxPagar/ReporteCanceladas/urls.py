from django.urls import path
from . import views

urlpatterns = [
    path('ReporteCanceladas', views.ReporteCanceladas, name='ReporteCanceladas'),
]

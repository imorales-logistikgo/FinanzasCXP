from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartaNoAdeudo, name="CartaNoAdeudo"),
]

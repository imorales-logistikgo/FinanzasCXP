from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.CartaNoAdeudo, name="CartaNoAdeudo"),
    path("GetCartaNoAdeudo", views.GetCartaNoAdeudo, name="GetCartaNoAdeudo"),
    path("SaveCartaNoAdeudo", views.SaveCartaNoAdeudo, name="SaveCartaNoAdeudo"),
    path("AprobarCarta", views.AprobarCarta, name="AprobarCarta"),
    path("RechazarCarta", views.RechazarCarta, name="RechazarCarta"),
    path("upload", views.upload, name="upload"),
    # path("desc", views.desc, name="desc"),
]

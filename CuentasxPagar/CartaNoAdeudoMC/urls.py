from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.CartaNoAdeudoMC, name="CartaNoAdeudoMC"),
    path('CreateCartaNoadeudoMC', views.CreateCartaNoadeudoMC, name='CreateCartaNoadeudoMC'),
    path('SaveCartaNoAdeudo', views.SaveCartaNoAdeudo, name='SaveCartaNoAdeudo'),
    path("upload", views.upload, name="upload"),
]
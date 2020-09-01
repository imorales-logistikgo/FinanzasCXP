from django.db import models
from usersadmon.models import AdmonUsuarios, Proveedor

class CartaNoAdeudoTransportistas(models.Model):
    IDCartaNoAdeudo = models.AutoField(primary_key=True)
    IDTransportista = models.ForeignKey(Proveedor, on_delete=models.CASCADE, db_column = 'IDTransportista')
    IDUsuarioAlta = models.IntegerField()
    IDUsuarioAprueba = models.IntegerField(default=None)
    IDUsuarioRechaza = models.IntegerField(default=None)
    FechaAlta = models.DateTimeField()
    MesCartaNoAdeudo = models.CharField(max_length=50)
    FechaAprueba = models.DateTimeField(default=None)
    FechaRechaza = models.DateTimeField(default=None)
    RutaCartaNoAdeudo = models.CharField(max_length=200)
    Status = models.CharField(max_length=100)
    ComentarioRechazo = models.CharField(max_length=300, default=None)

    class Meta:
        db_table = "CartaNoAdeudoTransportistas"
        managed = False


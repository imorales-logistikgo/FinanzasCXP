from django.db import models
from usersadmon.models import Proveedor


class LogStatusTransportista(models.Model):
    IDLogStatusTransportista = models.AutoField(primary_key=True)
    IDTransportista = models.ForeignKey(Proveedor, on_delete=models.CASCADE, db_column="IDTransportista")
    IDUsuarioAlta = models.IntegerField()
    StatusAnterior = models.CharField(max_length=15)
    StatusActual = models.CharField(max_length=15)
    FechaCambio = models.DateTimeField()

    class Meta:
        db_table = "LogStatusTransportista"
        managed = False
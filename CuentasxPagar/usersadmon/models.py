import base64
from django.db import models
import binascii

class AdmonUsuarios(models.Model):
    idusuario = models.AutoField(db_column='IDUsuario', primary_key=True)  # Field name made lowercase.
    nombreusuario = models.CharField(db_column='NombreUsuario', max_length=200, blank=True, null=True)  # Field name made lowercase.
    nombre = models.CharField(db_column='Nombre', max_length=200, blank=True, null=True)  # Field name made lowercase.
    apepaterno = models.CharField(db_column='ApePaterno', max_length=100, blank=True, null=True)  # Field name made lowercase.
    apematerno = models.CharField(db_column='ApeMaterno', max_length=100, blank=True, null=True)  # Field name made lowercase.
    correo = models.CharField(db_column='Correo', max_length=200, blank=True, null=True)  # Field name made lowercase.
    fechacambiocontrasena = models.DateTimeField(db_column='FechaCambioContrasena', blank=True, null=True)  # Field name made lowercase.
    hasbytes = models.BinaryField(db_column='HasBytes', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    saltbytes = models.BinaryField(db_column='SaltBytes', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    periodo = models.IntegerField(db_column='Periodo', blank=True, null=True)  # Field name made lowercase.
    statusreg = models.CharField(db_column='StatusReg', max_length=20, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'AdmonUsuarios'



class Proveedor(models.Model):
    IDTransportista = models.AutoField(primary_key=True)
    NombreComercial = models.CharField(max_length=200)
    RazonSocial = models.CharField(max_length=200)
    RFC = models.CharField(max_length=200)
    Correo = models.CharField(db_column='Correo', max_length=200, blank=True, null=True)
    IsAmericano = models.BooleanField()
    Serie = models.CharField(max_length=15)
    FechaDescargaCartaNoAdeudo = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'AdmonTransportistas'

class AdmonCorreosxTransportista(models.Model):
    IDCorreoxTransportista = models.AutoField(primary_key=True)
    IDTransportista = models.ForeignKey(Proveedor, on_delete=models.CASCADE, db_column = 'IDTransportista')
    Correo = models.CharField(max_length=500)
    IsEnviarCorreo = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'AdmonCorreosxTransportista'

from django.db import models

class Bro_Viajes(models.Model):
    IDBro_Viaje = models.AutoField(db_column='IDBro_Viaje', primary_key=True)
    Folio = models.CharField(max_length=100)
    CostoViaje = models.DecimalField(db_column='CostoViaje',default=0, max_digits=30, decimal_places=5)
    CostoRecoleccion = models.DecimalField(db_column='CostoTotalRecoleccion',default=0, max_digits=30, decimal_places=5)
    CostoServicios = models.DecimalField(db_column='CostoServicios',default=0, max_digits=30, decimal_places=5)
    CostoTotalRepartos = models.DecimalField(db_column='CostoTotalRepartos',default=0, max_digits=30, decimal_places=5)
    CostoSubtotal = models.DecimalField(db_column='CostoSubtotal',default=0, max_digits=30, decimal_places=5)
    CostoIVA = models.DecimalField(db_column='CostoIVA',default=0, max_digits=30, decimal_places=5)
    CostoRetencion = models.DecimalField(db_column='CostoRetencion',default=0, max_digits=30, decimal_places=5)
    CostoTotal = models.DecimalField(db_column='CostoTotal',default=0, max_digits=30, decimal_places=5)
    Tipo = models.CharField(max_length=100)
    Remisiones = models.CharField(max_length=500)
    StatusProceso = models.CharField(max_length=200)
    IsEvidenciasDigitales = models.BooleanField()
    IsEvidenciasFisicas = models.BooleanField()
    FechaDescarga = models.DateTimeField(db_column = 'FechaDescarga')
    IDTransportista = models.IntegerField()
    RutaHojaLiberacion = models.CharField(max_length=500)
    IsDescargaHojaLiberacion = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'Bro_Viajes'

class Bro_ServiciosxViaje(models.Model):
    Bro_IDServicioxViaje = models.AutoField(db_column='Bro_IDServicioxViaje', primary_key=True)
    IDBro_Servicio = models.IntegerField()
    IDBro_Viaje = models.IntegerField()
    Costo = models.DecimalField(db_column='Costo',default=0, max_digits=30, decimal_places=5)

    class Meta:
        managed = False
        db_table = 'Bro_ServiciosxViaje'


class Servicios(models.Model):
    IDservicio = models.AutoField(db_column='IDservicio', primary_key=True)
    Nombre = models.CharField(max_length=100)
    IsAplicaiva = models.BooleanField()
    IsAplicaRetencion = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'Servicios'


class Bro_RepartosxViaje(models.Model):
    IDBro_RepartoxViaje = models.AutoField(db_column='IDBro_RepartoxViaje', primary_key=True)
    IDBro_Viaje = models.IntegerField()
    IDCliente = models.IntegerField()
    CostoReparto = models.DecimalField(db_column='CostoReparto',default=0, max_digits=30, decimal_places=5)

    class Meta:
        managed = False
        db_table = 'Bro_RepartosxViaje'

class Clientes(models.Model):
    IDCliente = models.AutoField(db_column='IDCliente', primary_key=True)
    Estado = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Clientes'

class Bro_EvidenciasxViaje(models.Model):
    IDBro_EvidenciaxViaje = models.AutoField(primary_key=True)
    IDBro_Viaje = models.ForeignKey(Bro_Viajes, on_delete=models.CASCADE, db_column = 'IDBro_Viaje')
    FechaCaptura = models.DateTimeField()
    FechaValidacion = models.DateTimeField()
    FechaRechazo = models.DateTimeField()
    Titulo = models.CharField(max_length=200)
    Tipo = models.CharField(max_length=200)
    NombreArchivo = models.CharField(max_length=200)
    RutaArchivo = models.CharField(max_length=300)
    Observaciones = models.CharField(max_length=200)
    ComentarioRechazo = models.CharField(max_length=200)
    IsValidada = models.BooleanField(default=0)
    IsRechazada = models.BooleanField(default=0)
    IsRemplazada = models.BooleanField(default=0)
    IsProyectoEspecial = models.BooleanField(default=0)
    IsEnviada = models.BooleanField()
    IsEvidenciaFisicaAprobada = models.BooleanField(default = 0)

    class Meta:
        managed = False
        db_table = 'Bro_EvidenciasxViaje'

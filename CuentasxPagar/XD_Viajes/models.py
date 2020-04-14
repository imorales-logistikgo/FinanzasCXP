from django.db import models

class XD_Viajes(models.Model):
    XD_IDViaje = models.AutoField(db_column='XD_IDViaje', primary_key=True)
    Folio = models.CharField(max_length=100)
    Costo = models.DecimalField(db_column='Costo',default=0, max_digits=30, decimal_places=5)
    CostoRepartos = models.DecimalField(db_column='CostoRepartos',default=0, max_digits=30, decimal_places=5)
    CostoSubtotal = models.DecimalField(db_column='CostoSubtotal',default=0, max_digits=30, decimal_places=5)
    CostoAccesorios = models.DecimalField(db_column='CostoAccesorios',default=0, max_digits=30, decimal_places=5)
    CostoIVA = models.DecimalField(db_column='CostoIVA',default=0, max_digits=30, decimal_places=5)
    CostoRetencion = models.DecimalField(db_column='CostoRetencion',default=0, max_digits=30, decimal_places=5)
    CostoTotal = models.DecimalField(db_column='CostoTotal',default=0, max_digits=30, decimal_places=5)
    Status = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'XD_Viajes'


class XD_AccesoriosxViajes(models.Model):
    XD_IDAccesorioxViaje = models.AutoField(db_column='XD_IDAccesorioxViaje', primary_key=True)
    XD_IDViaje = models.IntegerField(db_column='XD_IDViaje')
    Descripcion = models.CharField(db_column='Descripcion', max_length=100)
    Costo = models.DecimalField(db_column='Costo',default=0, max_digits=30, decimal_places=5)

    class Meta:
        managed= False
        db_table = 'XD_AccesoriosxViajes'


class RepartosxViaje(models.Model):
    IDRepartoxViaje = models.AutoField(db_column='IDRepartoxViaje', primary_key=True)
    XD_IDViaje = models.IntegerField()
    Costo = models.DecimalField(db_column='Costo',default=0, max_digits=30, decimal_places=5)
    Estado = models.CharField(db_column='Estado', max_length=100)
    Numero = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'RepartosxViaje'
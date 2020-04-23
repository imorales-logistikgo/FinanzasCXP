from django.db import models
from usersadmon.models import AdmonUsuarios

class PendientesEnviar(models.Model):
    IDPendienteEnviar = models.AutoField(primary_key=True)
    Folio = models.CharField(max_length=50, unique=True)
    NombreCortoCliente = models.CharField(max_length=100)
    NombreCortoProveedor = models.CharField(max_length=100)
    FechaDescarga = models.DateTimeField()
    Moneda = models.CharField(max_length=10)
    #Costo = models.FloatField(default=0)
    #Precio = models.FloatField(default=0)
    Status = models.CharField(max_length=15)
    IsEvidenciaFisica = models.BooleanField()
    IsEvidenciaDigital = models.BooleanField()
    Proyecto = models.CharField(max_length=30)
    TipoConcepto = models.CharField(max_length=30)

    def __str__(self):
        return str(self.IDPendienteEnviar)
    class Meta:
        db_table="PendientesEnviar"
        managed= False


class Ext_PendienteEnviar_Costo(models.Model):
    IDPendienteEnviar = models.OneToOneField(PendientesEnviar, on_delete=models.CASCADE, db_column = 'IDPendienteEnviar', primary_key=True)
    CostoSubtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    CostoIVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    CostoRetencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    CostoTotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IsFacturaProveedor = models.BooleanField(default=False)
    class Meta:
        db_table="Ext_PendienteEnviar_Costo"
        managed= False


class Ext_PendienteEnviar_Precio(models.Model):
    IDPendienteEnviar = models.OneToOneField(PendientesEnviar, on_delete=models.CASCADE, db_column = 'IDPendienteEnviar', primary_key=True)
    PrecioSubtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    PrecioIVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    PrecioRetencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    PrecioTotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    PrecioServicios = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IsFacturaCliente = models.BooleanField(default=False)
    class Meta:
        db_table="Ext_PendienteEnviar_Precio"
        managed= False



class RelacionConceptoxProyecto(models.Model):
    IDRelacionConceptoxProyecto = models.AutoField(primary_key=True)
    IDPendienteEnviar = models.ForeignKey(PendientesEnviar, on_delete=models.CASCADE, db_column = 'IDPendienteEnviar')
    IDConcepto = models.IntegerField(default=0)
    IDCliente = models.IntegerField(default=0)
    IDProveedor = models.IntegerField(default=0)

    class Meta:
        db_table="RelacionConceptoxProyecto"
        managed= False


class View_PendientesEnviarCxP(models.Model):
    IDPendienteEnviar = models.IntegerField(primary_key=True)
    IDConcepto = models.IntegerField(default=0)
    Folio = models.CharField(max_length=10, unique=True)
    IDProveedor = models.IntegerField(default=0)
    NombreProveedor = models.CharField(max_length=100)
    FechaDescarga = models.DateTimeField()
    Subtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Retencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Total = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Moneda = models.CharField(max_length=10)
    Status = models.CharField(max_length=15)
    IsEvidenciaDigital = models.BooleanField()
    IsEvidenciaFisica = models.BooleanField()
    Proyecto = models.CharField(max_length=30)
    IsFacturaProveedor = models.BooleanField()
    IsControlDesk = models.BooleanField()
    class Meta:
        managed = False
        db_table = "View_PendientesEnviarCxP"
    def str(self):
        return self.IDPendienteEnviar


class FacturasxProveedor(models.Model):
    IDFactura = models.AutoField(primary_key=True)
    Folio = models.CharField(db_column='Folio', max_length=50)
    NombreCortoProveedor = models.CharField(max_length=100)
    IDProveedor = models.IntegerField(default=0)
    FechaFactura = models.DateTimeField()
    FechaRevision = models.DateTimeField()
    FechaVencimiento = models.DateTimeField()
    Moneda = models.CharField(max_length=10)
    Subtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Retencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Total = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Saldo = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IsAutorizada = models.BooleanField(default=False)
    RutaXML = models.CharField(max_length=300)
    RutaPDF = models.CharField(max_length=300)
    TipoCambio = models.DecimalField(default=0, max_digits=10, decimal_places=5)
    Comentarios = models.CharField(max_length=500)
    TotalConvertido = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Status = models.CharField(max_length=15, default="PENDIENTE")
    IDUsuarioAlta = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column = 'IDUsuarioAlta', related_name = "IDUsuarioAltaFactura")
    IDUsuarioBaja = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column = 'IDUsuarioBaja', related_name = "IDUsuarioBajaFactura", null=True)
    TotalXML = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    ComentarioBaja = models.CharField(max_length=500)

    # def __str__(self):
    #     return str(self.IDFactura)
    class Meta:
        db_table = "FacturasxProveedor"
        managed = False


class PartidaProveedor(models.Model):
    IDPartida = models.AutoField(primary_key=True)
    FechaAlta = models.DateTimeField()
    FechaBaja = models.DateTimeField(null=True, blank=True)
    Subtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Retencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Total = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IsActiva = models.BooleanField(default=True)

    class Meta:
        db_table = "PartidaProveedor"


class RelacionFacturaProveedorxPartidas(models.Model):
    IDRelacionFacturaxPartidas = models.AutoField(primary_key=True)
    IDFacturaxProveedor = models.ForeignKey(FacturasxProveedor, on_delete=models.CASCADE, db_column = 'IDFacturaxProveedor', related_name='FacturaxPartidas')
    IDPartida = models.ForeignKey(PartidaProveedor, on_delete=models.CASCADE, db_column = 'IDPartida')
    IDPendienteEnviar = models.ForeignKey(PendientesEnviar, on_delete=models.CASCADE, db_column = 'IDPendienteEnviar')

    class Meta:
        db_table = "RelacionFacturaProveedorxPartidas"

from django.db import models
from PendientesEnviar.models import FacturasxProveedor
from usersadmon.models import AdmonUsuarios

class PagosxFacturas(models.Model):
    IDPagoxFactura = models.AutoField(primary_key=True)
    FechaAlta = models.DateTimeField()
    Total = models.DecimalField(default=0, max_digits=30, decimal_places=5)

    class Meta:
        db_table="PagosxFacturas"


class PagosxProveedor(models.Model):
    IDPago = models.AutoField(primary_key=True)
    FechaAlta = models.DateTimeField()
    FechaBaja = models.DateTimeField(null = True)
    Total = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Folio = models.CharField(max_length=50)
    RutaPDF = models.CharField(max_length=300)
    RutaXML = models.CharField(max_length=300)
    RutaComprobante = models.CharField(max_length=300)
    FechaPago = models.DateTimeField()
    Comentarios = models.CharField(max_length=500, default = "")
    TipoCambio = models.DecimalField(default=1, max_digits=10, decimal_places=5)
    NombreCortoProveedor = models.CharField(max_length=100)
    Status = models.CharField(max_length=15)
    IDUsuarioAlta = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column = 'IDUsuarioAlta', related_name = "IDUsuarioAlta")
    IDUsuarioBaja = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column = 'IDUsuarioBaja', related_name = "IDUsuarioBaja", null=True)
    IDProveedor = models.IntegerField(default=0)
    ComentarioBaja = models.CharField(max_length=500, default = "")

    class Meta:
        db_table="PagosxProveedor"



class RelacionPagosFacturasxProveedor(models.Model):
    IDRelacionPagoFacturasxProveedor = models.AutoField(primary_key=True)
    IDPago = models.ForeignKey(PagosxProveedor, on_delete=models.CASCADE, db_column = 'IDPago')
    IDPagoxFactura = models.ForeignKey(PagosxFacturas, on_delete=models.CASCADE, db_column = 'IDPagoxFactura')
    IDFactura = models.ForeignKey(FacturasxProveedor, on_delete=models.CASCADE, db_column = 'IDFactura')

    class Meta:
        db_table="RelacionPagosFacturasxProveedor"



class View_FacturasxProveedor(models.Model):
    IDFactura = models.IntegerField(primary_key=True)
    Folio = models.CharField(max_length=50)
    Proveedor = models.CharField(max_length=100)
    IDProveedor = models.IntegerField(default=0)
    FechaFactura = models.DateTimeField()
    Subtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Retencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Total = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Saldo = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    RutaXML = models.CharField(max_length=300)
    Status = models.CharField(max_length=15)
    IsAutorizada = models.BooleanField()
    Moneda = models.CharField(max_length=10)
    TotalXML = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    FolioPago = models.CharField(max_length=50)
    StatusPago = models.CharField(max_length=50)

    class Meta:
        db_table = "View_FacturasxProveedor"
        managed= False


class HistorialReajusteProveedor(models.Model):
    IDHistorialReajuste = models.AutoField(primary_key = True)
    IDPendienteEnviar = models.IntegerField()
    IDFacturaxProveedor = models.IntegerField()
    CostoSubtotalAnterior = models.DecimalField(max_digits=30, decimal_places=5,  default =0)
    CostoIVAAnterior = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    CostoRetencionAnterior = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    CostoTotalAnterior = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    NuevoCosto = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    NuevoCostoRepartos = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    NuevoCostoAccesorios = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    NuevoCostoSubtotal = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    NuevoCostoIVA = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    NuevoCostoRetencion = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    NuevoCostoTotal = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    FechaAlta = models.DateTimeField()
    IDUsuarioAlta = models.IntegerField()
    NuevoCostoRecoleccion = models.DecimalField(max_digits=30, decimal_places=5, default =0)
    Motivo = models.CharField(max_length=500, default = "")

    class Meta:
        db_table = "HistorialReajusteProveedor"
        managed = False

class TempSerie(models.Model):
    RazonSocial = models.CharField(max_length=500)
    Serie = models.CharField(max_length=15)

    class Meta:
        db_table = "TempSerie"
        managed = False

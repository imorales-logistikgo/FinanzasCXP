from django.db import models
from usersadmon.models import AdmonUsuarios

class View_Master_Proveedor(models.Model):
    IDPendienteEnviar = models.IntegerField(primary_key=True)
    Folio = models.CharField(max_length=10, unique=True)
    NombreCortoCliente = models.CharField(max_length=100)
    NombreCortoProveedor = models.CharField(max_length=100)
    FechaDescarga = models.DateTimeField()
    Moneda = models.CharField(max_length=10)
    Status = models.CharField(max_length=15)
    IsEvidenciaDigital = models.BooleanField()
    IsEvidenciaFisica = models.BooleanField()
    Proyecto = models.CharField(max_length=30)
    TipoConcepto = models.CharField(max_length=30)
    IsControlDesk = models.BooleanField()
    CostoSubtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    CostoIVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    CostoRetencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    CostoTotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IsFacturaProveedor = models.BooleanField()
    FolioFactProveedor = models.CharField(max_length=50)
    MOP = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    PrecioSubtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    PrecioIVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    PrecioRetencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    PrecioTotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IsFacturaCliente = models.BooleanField()
    FolioFactCliente = models.CharField(max_length=50)
    IDProveedor = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "View_Master_Proveedor"

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
    SubtotalC = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IVAC = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    RetencionC = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    TotalC = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IsFacturaProveedor = models.BooleanField()
    FolioFactProveedor = models.CharField(max_length=50)
    StatusFacturaProveedor = models.CharField(max_length=50)
    MOP = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Subtotal = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IVA = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Retencion = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    Total = models.DecimalField(default=0, max_digits=30, decimal_places=5)
    IsFacturaCliente = models.BooleanField()
    FolioFactCliente = models.CharField(max_length=50)
    StatusFacturaCliente = models.CharField(max_length=50)
    IDProveedor = models.IntegerField(default=0)

    class Meta:
        db_table = "View_Master_Proveedor"
        managed = False

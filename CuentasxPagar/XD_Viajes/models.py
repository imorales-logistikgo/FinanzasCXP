from django.db import models
from usersadmon.models import AdmonUsuarios, Proveedor


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
    IsEvidencia = models.BooleanField()
    IsEvidenciaPedidos = models.BooleanField()
    IsEvidenciaFisica = models.BooleanField()
    Status = models.CharField(max_length=100)
    TipoViaje = models.CharField(max_length=100)
    FechaDespacho = models.DateTimeField()
    IDTransportista = models.IntegerField()
    RutaHojaEmbarqueCosto= models.CharField(max_length=500)
    IsDescargaHojaLiberacion = models.BooleanField()
    FechaEvidenciaDigital = models.DateTimeField()
    FechaEvidenciaFisica = models.DateTimeField()
    FechaAlta = models.DateTimeField()
    IDClienteFiscal = models.IntegerField()

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

class XD_Pedidos(models.Model):
    XD_IDPedido = models.AutoField(primary_key=True)
    Delivery = models.CharField(max_length=100)
    IDClienteFiscal = models.IntegerField()
    Observaciones = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'XD_Pedidos'

class XD_PedidosxViajes(models.Model):
    XD_PedidoxViaje = models.AutoField(primary_key=True)
    XD_IDPedido = models.ForeignKey(XD_Pedidos, on_delete=models.CASCADE, db_column='XD_IDPedido')
    XD_IDViaje = models.ForeignKey(XD_Viajes, on_delete=models.CASCADE, db_column='XD_IDViaje')
    IsEvidenciaPedidoxViaje = models.BooleanField()
    IsEvidenciaFisicaPedidoxViaje = models.BooleanField()
    StatusPedido = models.CharField(max_length = 100)
    TipoTransporte = models.CharField(max_length = 100)
    IDUsuarioEvDigital = models.IntegerField()
    IDUsuarioEvFisica = models.IntegerField()
    FechaEvidenciaFisicaxPedidoxViaje = models.DateTimeField()
    FechaEvidenciaDigitalxPedidoxViaje = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'XD_PedidosxViajes'

class XD_EvidenciasxPedido(models.Model):
    IDEvidenciaxPedido = models.AutoField(db_column='IDXD_EvidenciaxPedido', primary_key = True)
    IDXD_Pedido = models.IntegerField() #ForeignKey(XD_Pedidos, on_delete=models.CASCADE, db_column='XD_IDPedido')
    XD_IDViaje = models.IntegerField() #ForeignKey(XD_Viajes, on_delete=models.CASCADE, db_column='XD_IDViaje')
    IDUsuarioAlta = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column = 'IDUsuarioAlta')
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
    IDUsuarioRechaza = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'XD_EvidenciasxPedido'


class ServiciosXD(models.Model):
    IDServicio = models.AutoField(primary_key=True)
    FechaAlta = models.DateTimeField()
    IDUsuarioAlta = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column='IDUsuarioAlta')
    IDTransportista = models.ForeignKey(Proveedor, on_delete=models.CASCADE, db_column='IDTransportista')
    Folio = models.CharField(max_length=100)
    StatusProceso = models.CharField(max_length=50)
    IsEvidenciaServicio = models.BooleanField()
    IsEvidenciaFisica = models.BooleanField()
    FechaEvidenciaDigital = models.DateTimeField()
    FechaEvidenciaFisica = models.DateTimeField()
    IsDescargaHojaLiberacion = models.BooleanField()
    RutaHojaEmbarqueCosto = models.CharField(max_length=300)
    class Meta:
        managed = False
        db_table = 'Servicios'




class XD_EvidenciasxViaje(models.Model):
    IDEvidenciaxViaje = models.AutoField(db_column='IDXD_EvidenciaxViaje', primary_key = True)
    IDXD_Pedido = models.IntegerField() #ForeignKey(XD_Pedidos, on_delete=models.CASCADE, db_column='XD_IDPedido')
    IDXD_Viaje = models.IntegerField() #ForeignKey(XD_Viajes, on_delete=models.CASCADE, db_column='XD_IDViaje')
    IDUsuarioAlta = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column = 'IDUsuarioAlta')
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
    IsRemplazada = models.BooleanField()
    IsProyectoEspecial = models.BooleanField()
    IsEnviada = models.BooleanField()
    IsEvidenciaFisicaAprobada = models.BooleanField(default = 0)
    IDUsuarioEvDigital = models.IntegerField()
    IDUsuarioEvFisica = models.IntegerField()
    FechaEvidenciaFisicaxPedidoxViaje = models.DateTimeField()
    IDUsuarioRechaza = models.IntegerField()
    IDServicio = models.ForeignKey(ServiciosXD, on_delete=models.CASCADE, db_column='IDServicio')

    class Meta:
        managed = False
        db_table = 'XD_EvidenciasxViaje'

class Ext_Viajes_MesaControl(models.Model):
    XD_IDViaje = models.OneToOneField(XD_Viajes, on_delete=models.CASCADE, db_column='XD_IDViaje', primary_key=True)
    IDUsuarioCXP = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column='IDUsuarioCXP', related_name="IDUsuarioCXP")
    IDUsuarioMC = models.ForeignKey(AdmonUsuarios, on_delete=models.CASCADE, db_column='IDUsuarioMC',related_name="IDUsuarioMC")
    IsDescargaHojaLiberacionCXP = models.BooleanField()
    IsDescargaHojaLiberacionMC = models.BooleanField()
    FechaDescargaHojaLiberacionCXP = models.DateTimeField()
    FechaDescargaHojaLiberacionMC = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Ext_Viajes_MesaControl'




# Generated by Django 2.1.13 on 2019-12-04 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PendientesEnviar',
            fields=[
                ('IDPendienteEnviar', models.AutoField(primary_key=True, serialize=False)),
                ('Folio', models.CharField(max_length=10, unique=True)),
                ('NombreCortoCliente', models.CharField(max_length=100)),
                ('NombreCortoProveedor', models.CharField(max_length=100)),
                ('FechaDescarga', models.CharField(max_length=100, null=True)),
                ('Moneda', models.CharField(max_length=10)),
                ('CostoSubtotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('CostoIVA', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('CostoRetencion', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('CostoTotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('PrecioSubtotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('PrecioIVA', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('PrecioRetencion', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('PrecioTotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Status', models.CharField(max_length=15)),
                ('IsFacturaCliente', models.BooleanField()),
                ('IsFacturaProveedor', models.BooleanField()),
                ('IsEvidenciaFisica', models.BooleanField()),
                ('IsEvidenciaDigital', models.BooleanField()),
            ],
            options={
                'db_table': 'PendientesEnviar',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RelacionConceptoxProyecto',
            fields=[
                ('RelacionIDConceptoxProyecto', models.AutoField(primary_key=True, serialize=False)),
                ('IDConcepto', models.IntegerField(default=0)),
                ('IDCliente', models.IntegerField(default=0)),
                ('IDProveedor', models.IntegerField(default=0)),
                ('Proyecto', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'RelacionConceptoxProyecto',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='FacturasxProveedor',
            fields=[
                ('IDFactura', models.AutoField(primary_key=True, serialize=False)),
                ('Folio', models.CharField(max_length=50, unique=True)),
                ('NombreCortoProveedor', models.CharField(max_length=100)),
                ('FechaFactura', models.DateTimeField()),
                ('FechaRevision', models.DateTimeField()),
                ('FechaVencimiento', models.DateTimeField()),
                ('Moneda', models.CharField(max_length=10)),
                ('Subtotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('IVA', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Retencion', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Total', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Saldo', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('IsAutorizada', models.BooleanField(default=False)),
                ('RutaXML', models.CharField(max_length=300)),
                ('RutaPDF', models.CharField(max_length=300)),
                ('TipoCambio', models.DecimalField(decimal_places=5, default=0, max_digits=10)),
                ('Comentarios', models.CharField(max_length=500)),
                ('TotalConvertido', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Status', models.CharField(default='PENDIENTE', max_length=15)),
            ],
            options={
                'db_table': 'FacturasxProveedor',
            },
        ),
        migrations.CreateModel(
            name='PartidaProveedor',
            fields=[
                ('IDPartida', models.AutoField(primary_key=True, serialize=False)),
                ('FechaAlta', models.DateTimeField()),
                ('FechaBaja', models.DateTimeField(blank=True, null=True)),
                ('Subtotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('IVA', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Retencion', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Total', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('IsActiva', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'PartidaProveedor',
            },
        ),
        migrations.CreateModel(
            name='RelacionFacturaProveedorxPartidas',
            fields=[
                ('IDRelacionFacturaxPartidas', models.AutoField(primary_key=True, serialize=False)),
                ('IDConcepto', models.IntegerField(default=0)),
                ('IDUsuarioAlta', models.IntegerField(default=0)),
                ('IDUsuarioBaja', models.IntegerField(default=0)),
                ('IDFacturaxProveedor', models.ForeignKey(db_column='IDFacturaxCliente', on_delete=django.db.models.deletion.CASCADE, to='PendientesEnviar.FacturasxProveedor')),
                ('IDPartida', models.ForeignKey(db_column='IDPartida', on_delete=django.db.models.deletion.CASCADE, to='PendientesEnviar.PartidaProveedor')),
            ],
            options={
                'db_table': 'RelacionFacturaProveedorxPartidas',
            },
        ),
        migrations.CreateModel(
            name='View_PendientesEnviarCxP',
            fields=[
                ('IDPendienteEnviar', models.OneToOneField(db_column='IDPendienteEnviar', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='PendientesEnviar.PendientesEnviar')),
                ('IDConcepto', models.IntegerField(default=0)),
                ('Folio', models.CharField(max_length=10, unique=True)),
                ('IDProveedor', models.IntegerField(default=0)),
                ('NombreProveedor', models.CharField(max_length=100)),
                ('FechaDescarga', models.DateTimeField()),
                ('CostoSubtotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('CostoIVA', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('CostoRetencion', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('CostoTotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Moneda', models.CharField(max_length=10)),
                ('Status', models.CharField(max_length=15)),
                ('IsEvidenciaDigital', models.BooleanField()),
                ('IsEvidenciaFisica', models.BooleanField()),
                ('Proyecto', models.CharField(max_length=30)),
                ('IsFacturaCliente', models.BooleanField()),
                ('IsFacturaProveedor', models.BooleanField()),
            ],
            options={
                'db_table': 'View_PendientesEnviarCxP',
                'managed': False,
            },
        ),
    ]

# Generated by Django 2.1.13 on 2019-12-05 21:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('PendientesEnviar', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='View_FacturasxProveedor',
            fields=[
                ('IDFactura', models.IntegerField(primary_key=True, serialize=False)),
                ('Folio', models.CharField(max_length=50)),
                ('Proveedor', models.CharField(max_length=100)),
                ('FechaFactura', models.DateTimeField()),
                ('Subtotal', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('IVA', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Retencion', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Total', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Saldo', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('RutaXML', models.CharField(max_length=300)),
                ('Status', models.CharField(max_length=15)),
                ('IsAutorizada', models.BooleanField()),
                ('Moneda', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'View_FacturasxProveedor',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='CobrosxFacturasProveedor',
            fields=[
                ('IDCobroxFactura', models.AutoField(primary_key=True, serialize=False)),
                ('FechaAlta', models.DateTimeField()),
                ('Total', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
            ],
            options={
                'db_table': 'CobrosxFacturasProveedor',
            },
        ),
        migrations.CreateModel(
            name='CobrosxProveedor',
            fields=[
                ('IDCobro', models.AutoField(primary_key=True, serialize=False)),
                ('FechaAlta', models.DateTimeField()),
                ('Total', models.DecimalField(decimal_places=5, default=0, max_digits=30)),
                ('Folio', models.CharField(max_length=50, unique=True)),
                ('RutaPDF', models.CharField(max_length=300)),
                ('RutaXML', models.CharField(max_length=300)),
                ('FechaCobro', models.DateTimeField()),
                ('Comentarios', models.CharField(default='', max_length=500)),
                ('TipoCambio', models.DecimalField(decimal_places=5, default=1, max_digits=10)),
                ('NombreCortoProveedor', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'CobrosxProveedor',
            },
        ),
        migrations.CreateModel(
            name='RelacionCobrosFacturasxProveedor',
            fields=[
                ('IDRelacionCobroFacturasxProveedor', models.AutoField(primary_key=True, serialize=False)),
                ('IDUsuarioAlta', models.IntegerField(default=0)),
                ('IDProveedor', models.IntegerField(default=0)),
                ('IDCobro', models.ForeignKey(db_column='IDCobro', on_delete=django.db.models.deletion.CASCADE, to='EstadosCuenta.CobrosxProveedor')),
                ('IDCobroxFactura', models.ForeignKey(db_column='IDCobroxFactura', on_delete=django.db.models.deletion.CASCADE, to='EstadosCuenta.CobrosxFacturasProveedor')),
                ('IDFactura', models.ForeignKey(db_column='IDFactura', on_delete=django.db.models.deletion.CASCADE, to='PendientesEnviar.FacturasxProveedor')),
            ],
            options={
                'db_table': 'RelacionCobrosFacturasxProveedor',
            },
        ),
    ]
# Generated by Django 2.1.13 on 2020-01-06 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EstadosCuenta', '0005_auto_20200106_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagosxproveedor',
            name='RutaComprobante',
            field=models.CharField(default='http://lgklataforma.blob.core.windows.net/evidencias/05e2decb-08fb-4a5a-a4ff-4239f68420e5.xml', max_length=300),
            preserve_default=False,
        ),
    ]
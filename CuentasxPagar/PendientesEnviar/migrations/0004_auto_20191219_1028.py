# Generated by Django 2.1.13 on 2019-12-19 16:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PendientesEnviar', '0003_ext_pendienteenviar_costo_ext_pendienteenviar_precio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='relacionfacturaproveedorxpartidas',
            name='IDConcepto',
        ),
        migrations.AddField(
            model_name='relacionfacturaproveedorxpartidas',
            name='IDPendienteEnviar',
            field=models.ForeignKey(db_column='IDPendienteEnviar', default=1, on_delete=django.db.models.deletion.CASCADE, to='PendientesEnviar.PendientesEnviar'),
            preserve_default=False,
        ),
    ]
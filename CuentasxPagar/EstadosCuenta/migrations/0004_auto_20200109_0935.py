# Generated by Django 2.1.13 on 2020-01-09 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usersadmon', '0002_proveedor'),
        ('EstadosCuenta', '0003_auto_20200109_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagosxproveedor',
            name='IDUsuarioAlta',
            field=models.ForeignKey(db_column='IDUsuarioAlta', default=1, on_delete=django.db.models.deletion.CASCADE, related_name='IDUsuarioAlta', to='usersadmon.AdmonUsuarios'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pagosxproveedor',
            name='IDUsuarioBaja',
            field=models.ForeignKey(db_column='IDUsuarioBaja', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='IDUsuarioBaja', to='usersadmon.AdmonUsuarios'),
        ),
    ]

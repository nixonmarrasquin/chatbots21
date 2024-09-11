from django.db import models

class CabeceraChat(models.Model):
    idCabeceraChat = models.AutoField(primary_key=True)
    user = models.CharField(max_length=255, null=True)
    fecha = models.DateTimeField(null=True)

    class Meta:
        db_table = 'cabecerachat'

class DetalleChat(models.Model):
    idDetalleChat = models.AutoField(primary_key=True)
    idCabeceraChat = models.ForeignKey(CabeceraChat, on_delete=models.CASCADE, db_column='idCabeceraChat')
    mensaje = models.CharField(max_length=1000, null=True)
    idTipo = models.CharField(max_length=255, null=True)
    fechaMensaje = models.DateTimeField(null=True)

    class Meta:
        db_table = 'detallechat'

from django.db import models


class CabeceraChat(models.Model):
    idCabeceraChat = models.AutoField(primary_key=True)
    user = models.CharField(max_length=255, null=True)
    fecha = models.DateTimeField(null=True)
    ultimo_chat = models.DateTimeField(null=True)

    class Meta:
        db_table = 'cabecerachat'

    def __str__(self):
        return f"{self.user} - {self.fecha}"  # Ajusta esto según lo que desees mostrar

class DetalleChat(models.Model):
    idDetalleChat = models.AutoField(primary_key=True)
    idCabeceraChat = models.ForeignKey(CabeceraChat, on_delete=models.CASCADE, db_column='idCabeceraChat')
    mensaje = models.CharField(max_length=1000, null=True)
    idTipo = models.CharField(max_length=255, null=True)
    fechaMensaje = models.DateTimeField(null=True)

    def __str__(self):
        return f"Mensaje: {self.mensaje} (Fecha: {self.fechaMensaje})"

    class Meta:
        db_table = 'detallechat'


class CodigoOTP(models.Model):
    codigo_cliente = models.CharField(max_length=13)  # RUC o Cédula
    codigo_otp = models.CharField(max_length=4)       # Código OTP
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'codigootp'  # Cambiado para evitar la duplicación del nombre del esquema


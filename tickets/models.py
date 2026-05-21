import uuid
from django.db import models
from django.conf import settings
from events.models import Event

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('ACTIVA', 'Activa'),
        ('UTILIZADA', 'Utilizada'),
        ('CANCELADA', 'Cancelada'),
    )
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Comprador"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Evento"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Pagado")
    uuid_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="Código Único")
    qr_code = models.ImageField(upload_to="tickets/qr/", blank=True, null=True, verbose_name="Código QR")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVA', verbose_name="Estado de Entrada")
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"

    def __str__(self):
        return f"Ticket {self.uuid_code} - {self.event.title} ({self.buyer.username})"

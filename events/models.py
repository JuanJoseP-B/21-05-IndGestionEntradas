from django.db import models
from django.conf import settings

class Location(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nombre del Recinto")
    capacity = models.PositiveIntegerField(verbose_name="Capacidad Máxima")
    address = models.CharField(max_length=255, verbose_name="Dirección")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"

    def __str__(self):
        return f"{self.name} - {self.city} (Capacidad: {self.capacity})"

class Event(models.Model):
    STATUS_CHOICES = (
        ('BORRADOR', 'Borrador'),
        ('PUBLICADO', 'Publicado'),
        ('CANCELADO', 'Cancelado'),
    )
    title = models.CharField(max_length=200, verbose_name="Título del Evento")
    description = models.TextField(verbose_name="Descripción")
    date = models.DateField(verbose_name="Fecha")
    time = models.TimeField(verbose_name="Hora")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='BORRADOR', verbose_name="Estado")
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Organizador"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Ubicación"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def __str__(self):
        return f"{self.title} ({self.date})"

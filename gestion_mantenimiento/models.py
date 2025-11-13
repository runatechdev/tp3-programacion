from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class OrdenDeTrabajo(models.Model):
    """
    Modelo para representar las órdenes de trabajo del sistema.
    """

    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En Progreso', 'En Progreso'),
        ('Cerrada', 'Cerrada'),
    ]
    
    PRIORIDADES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
    ]
    
    # Campos principales
    titulo = models.CharField(
        max_length=200, 
        verbose_name="Título de la orden",
        help_text="Breve descripción del problema"
    )
    
    fecha = models.DateField(
        verbose_name="Fecha de reporte",
        help_text="Fecha en que se reporta la falla"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación en sistema"
    )
    
    descripcion_falla = models.TextField(
        verbose_name="Descripción de la falla",
        help_text="Describa en detalle la falla o problema (mínimo 20 caracteres)"
    )
    
    prioridad = models.CharField(
        max_length=10, 
        choices=PRIORIDADES, 
        default='Media',
        verbose_name="Nivel de prioridad"
    )
    
    estado = models.CharField(
        max_length=15, 
        choices=ESTADOS, 
        default='Pendiente',
        verbose_name="Estado actual"
    )
    
    # Relaciones con usuarios
    operario_creador = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ordenes_creadas',
        verbose_name="Operario que reporta"
    )
    
    operario_asignado = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ordenes_asignadas',
        verbose_name="Operario asignado"
    )
    
    fecha_cierre_real = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Fecha real de cierre"
    )
    
    class Meta:
        verbose_name = "Orden de Trabajo"
        verbose_name_plural = "Órdenes de Trabajo"
        ordering = ['-fecha_creacion']
        permissions = [
            ("can_close_order", "Puede cerrar órdenes de trabajo"),
        ]
    
    def __str__(self):
        return f"OT-{self.id}: {self.titulo} - {self.estado}"
    
    def get_absolute_url(self):
        return reverse('detalle_orden', kwargs={'pk': self.pk})
    
    @property
    def esta_cerrada(self):
        """Retorna True si la orden está cerrada"""
        return self.estado == 'Cerrada'
    
    @property
    def puede_consumir_suministros(self):
        """Retorna True si se pueden consumir suministros para esta orden"""
        return self.estado in ['Pendiente', 'En Progreso']
    
    def cerrar_orden(self):
        """Método para cerrar una orden"""
        if not self.fecha_cierre_real:
            self.fecha_cierre_real = timezone.now()
        self.estado = 'Cerrada'
        self.save()


class Suministro(models.Model):
    """
    Modelo para representar los suministros disponibles en inventario
    """
    
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del suministro",
        help_text="Ej: Tornillos M8, Aceite Motor, Filtro Aire"
    )
    
    descripcion = models.TextField(
        verbose_name="Descripción detallada",
        blank=True
    )
    
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad en stock",
        help_text="Cantidad disponible en inventario"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Precio unitario",
        help_text="Precio por unidad en moneda local"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de última actualización"
    )
    
    class Meta:
        verbose_name = "Suministro"
        verbose_name_plural = "Suministros"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock})"
    
    @property
    def stock_bajo(self):
        """Retorna True si el stock es menor a 10 unidades"""
        return self.stock < 10
    
    def reducir_stock(self, cantidad):
        """Reduce el stock en la cantidad especificada"""
        if cantidad <= self.stock:
            self.stock -= cantidad
            self.save()
            return True
        return False
    
    def aumentar_stock(self, cantidad):
        """Aumenta el stock en la cantidad especificada"""
        self.stock += cantidad
        self.save()


class ConsumoSuministro(models.Model):
    """
    Modelo para registrar el consumo de suministros en órdenes de trabajo
    """
    
    orden_de_trabajo = models.ForeignKey(
        OrdenDeTrabajo,
        on_delete=models.CASCADE,
        related_name='consumos',
        verbose_name="Orden de trabajo asociada"
    )
    
    suministro = models.ForeignKey(
        Suministro,
        on_delete=models.CASCADE,
        related_name='consumos',
        verbose_name="Suministro utilizado"
    )
    
    cantidad_usada = models.PositiveIntegerField(
        verbose_name="Cantidad utilizada",
        help_text="Cantidad consumida del suministro"
    )
    
    fecha_consumo = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del consumo"
    )
    
    operario_registra = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consumos_registrados',
        verbose_name="Operario que registra",
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Consumo de Suministro"
        verbose_name_plural = "Consumos de Suministros"
        ordering = ['-fecha_consumo']
        unique_together = ['orden_de_trabajo', 'suministro']
    
    def __str__(self):
        return f"{self.cantidad_usada} x {self.suministro.nombre} - {self.orden_de_trabajo.titulo}"
    
    def save(self, *args, **kwargs):
        """Override save para actualizar automáticamente el stock"""
        if self.pk is None:  # Solo si es nuevo consumo
            # Reducir el stock del suministro
            self.suministro.reducir_stock(self.cantidad_usada)
        super().save(*args, **kwargs)
    
    @property
    def costo_total(self):
        """Calcula el costo total del consumo"""
        return self.cantidad_usada * self.suministro.precio_unitario
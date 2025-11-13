from django.contrib import admin
from .models import OrdenDeTrabajo, Suministro, ConsumoSuministro

# Filtro personalizado para stock bajo
class StockBajoFilter(admin.SimpleListFilter):
    title = 'stock bajo'
    parameter_name = 'stock_bajo'

    def lookups(self, request, model_admin):
        return (
            ('si', 'Stock Bajo (<10)'),
            ('no', 'Stock Normal (≥10)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.filter(stock__lt=10)
        if self.value() == 'no':
            return queryset.filter(stock__gte=10)
        return queryset

@admin.register(OrdenDeTrabajo)
class OrdenDeTrabajoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'titulo', 'prioridad', 'estado', 'operario_creador', 
        'operario_asignado', 'fecha', 'fecha_creacion', 'fecha_cierre_real'
    ]
    list_filter = ['prioridad', 'estado', 'fecha_creacion', 'operario_creador']
    search_fields = ['titulo', 'descripcion_falla']
    readonly_fields = ['fecha_creacion']
    list_editable = ['estado', 'prioridad']
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'fecha', 'descripcion_falla', 'prioridad')
        }),
        ('Estado y Asignación', {
            'fields': ('estado', 'operario_creador', 'operario_asignado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_cierre_real')
        }),
    )

@admin.register(Suministro)
class SuministroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'stock', 'precio_unitario', 'es_stock_bajo', 'fecha_actualizacion']
    list_filter = [StockBajoFilter, 'fecha_actualizacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_actualizacion']
    
    fieldsets = (
        ('Información del Suministro', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Inventario y Precio', {
            'fields': ('stock', 'precio_unitario')
        }),
    )
    
    def es_stock_bajo(self, obj):
        """Método para mostrar si el stock está bajo en el list_display"""
        return obj.stock_bajo
    es_stock_bajo.boolean = True
    es_stock_bajo.short_description = 'Stock Bajo'

@admin.register(ConsumoSuministro)
class ConsumoSuministroAdmin(admin.ModelAdmin):
    list_display = ['suministro', 'cantidad_usada', 'orden_de_trabajo', 'operario_registra', 'fecha_consumo', 'costo_total_calculado']
    list_filter = ['fecha_consumo', 'operario_registra']
    readonly_fields = ['fecha_consumo']
    search_fields = ['suministro__nombre', 'orden_de_trabajo__titulo']
    
    fieldsets = (
        ('Información del Consumo', {
            'fields': ('orden_de_trabajo', 'suministro', 'cantidad_usada')
        }),
        ('Registro', {
            'fields': ('operario_registra', 'fecha_consumo')
        }),
    )
    
    def costo_total_calculado(self, obj):
        """Método para mostrar el costo total en el list_display"""
        return f"${obj.costo_total:.2f}"
    costo_total_calculado.short_description = 'Costo Total'
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestion_mantenimiento.urls')),
]

# Personalizar títulos del admin
admin.site.site_header = "MantenimientoFlow - Administración"
admin.site.site_title = "Sistema de Gestión de Mantenimiento"
admin.site.index_title = "Panel de Administración"
from django.urls import path
from . import views

app_name = 'gestion_mantenimiento'

urlpatterns = [
    # URLs de Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs Principales
    path('', views.lista_ordenes, name='lista_ordenes'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # URLs de Órdenes de Trabajo
    path('crear-orden/', views.crear_orden, name='crear_orden'),
    path('orden/<int:orden_id>/', views.detalle_orden, name='detalle_orden'),
    path('orden/<int:orden_id>/asignar/', views.asignar_orden, name='asignar_orden'),
    path('orden/<int:orden_id>/eliminar/', views.eliminar_orden, name='eliminar_orden'),
    
    # URLs de Suministros
    path('consumo-suministro/', views.consumo_suministro, name='consumo_suministro'),
]
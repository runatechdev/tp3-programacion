from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db import models
from .models import OrdenDeTrabajo, Suministro, ConsumoSuministro
from .forms import OrdenDeTrabajoForm, ConsumoSuministroForm, AsignacionYEstadoForm
from django.utils import timezone

# =============================================================================
# VISTAS DE AUTENTICACIÓN
# =============================================================================

def login_view(request):
    """
    Vista personalizada para login
    """
    if request.user.is_authenticated:
        return redirect('gestion_mantenimiento:lista_ordenes')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}!')
            
            # Redirigir según el grupo del usuario
            if user.groups.filter(name='Jefe de Taller').exists():
                return redirect('gestion_mantenimiento:lista_ordenes')
            elif user.groups.filter(name='Operario').exists():
                return redirect('gestion_mantenimiento:lista_ordenes')
            else:
                return redirect('gestion_mantenimiento:lista_ordenes')
                
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos.')
    
    return render(request, 'gestion_mantenimiento/login.html')

@login_required
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.info(request, '✅ Sesión cerrada correctamente.')
    return redirect('gestion_mantenimiento:login')  # CORREGIDO

# =============================================================================
# VISTA PRINCIPAL - LISTA DE ÓRDENES
# =============================================================================

@login_required
def lista_ordenes(request):
    """
    Vista principal que muestra las órdenes según el rol del usuario
    """
    # Guardar última orden vista en sesión (si se pasa por GET)
    orden_id = request.GET.get('ultima_orden_vista')
    if orden_id:
        request.session['ultima_orden_vista'] = orden_id
        messages.info(request, f'📌 Orden {orden_id} marcada como última vista.')
    
    # Filtrar órdenes según el rol del usuario
    if request.user.groups.filter(name='Operario').exists():
        # Operario ve solo sus órdenes creadas o asignadas
        ordenes = OrdenDeTrabajo.objects.filter(
            models.Q(operario_creador=request.user) | 
            models.Q(operario_asignado=request.user)
        ).order_by('-fecha_creacion')
        rol = "Operario"
        
    elif request.user.groups.filter(name='Jefe de Taller').exists():
        # Jefe de Taller ve todas las órdenes
        ordenes = OrdenDeTrabajo.objects.all().order_by('-fecha_creacion')
        rol = "Jefe de Taller"
        
    else:
        # Administrador ve todo
        ordenes = OrdenDeTrabajo.objects.all().order_by('-fecha_creacion')
        rol = "Administrador"
    
    # Filtrar por estado si se especifica
    estado_filtro = request.GET.get('estado')
    if estado_filtro:
        ordenes = ordenes.filter(estado=estado_filtro)
    
    context = {
        'ordenes': ordenes,
        'ultima_orden_vista': request.session.get('ultima_orden_vista'),
        'rol_usuario': rol,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'gestion_mantenimiento/lista_ordenes.html', context)

# =============================================================================
# FORMULARIO 1: CREAR ORDEN DE TRABAJO (OPERARIOS)
# =============================================================================

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Operario').exists(), 
                 login_url='/login/', 
                 redirect_field_name=None)
def crear_orden(request):
    """
    Vista para que los Operarios creen nuevas órdenes de trabajo
    """
    if request.method == 'POST':
        form = OrdenDeTrabajoForm(request.POST)
        if form.is_valid():
            try:
                orden = form.save(commit=False)
                orden.operario_creador = request.user
                orden.save()
                
                # Guardar en sesión la última orden creada
                request.session['ultima_orden_vista'] = orden.id
                request.session['ultima_orden_creada'] = orden.id
                
                messages.success(request, 
                    f'✅ ¡Orden de trabajo #{orden.id} creada exitosamente! '
                    f'Título: "{orden.titulo}"'
                )
                return redirect('gestion_mantenimiento:lista_ordenes')  # CORREGIDO
                
            except Exception as e:
                messages.error(request, f'❌ Error al crear la orden: {str(e)}')
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario.')
    else:
        form = OrdenDeTrabajoForm()
    
    context = {
        'form': form,
        'titulo_pagina': 'Crear Nueva Orden de Trabajo'
    }
    return render(request, 'gestion_mantenimiento/crear_orden.html', context)

# =============================================================================
# FORMULARIO 2: CONSUMO DE SUMINISTROS (OPERARIOS)
# =============================================================================

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Operario').exists(), 
                 login_url='/login/', 
                 redirect_field_name=None)
def consumo_suministro(request):
    """
    Vista para que los Operarios registren consumo de suministros
    """
    if request.method == 'POST':
        form = ConsumoSuministroForm(request.user, request.POST)
        if form.is_valid():
            try:
                consumo = form.save(commit=False)
                consumo.operario_registra = request.user
                
                # El stock se actualiza automáticamente en el save() del modelo
                consumo.save()
                
                messages.success(request,
                    f'✅ Consumo registrado exitosamente! '
                    f'{consumo.cantidad_usada} x {consumo.suministro.nombre} '
                    f'para orden #{consumo.orden_de_trabajo.id}. '
                    f'Stock restante: {consumo.suministro.stock}'
                )
                return redirect('gestion_mantenimiento:lista_ordenes')  # CORREGIDO
                
            except Exception as e:
                messages.error(request, f'❌ Error al registrar consumo: {str(e)}')
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario.')
    else:
        form = ConsumoSuministroForm(request.user)
    
    # Verificar si el usuario tiene órdenes asignadas
    tiene_ordenes_asignadas = OrdenDeTrabajo.objects.filter(
        operario_asignado=request.user,
        estado__in=['Pendiente', 'En Progreso']
    ).exists()
    
    context = {
        'form': form,
        'titulo_pagina': 'Registrar Consumo de Suministro',
        'tiene_ordenes_asignadas': tiene_ordenes_asignadas,
    }
    return render(request, 'gestion_mantenimiento/consumo_suministro.html', context)

# =============================================================================
# FORMULARIO 3: ASIGNACIÓN Y ESTADO (JEFES DE TALLER)
# =============================================================================

@login_required
def asignar_orden(request, orden_id):
    """
    Vista para que los Jefes de Taller asignen órdenes y cambien estados
    """
    # Verificar que el usuario sea Jefe de Taller
    if not request.user.groups.filter(name='Jefe de Taller').exists():
        messages.error(request, '❌ No tienes permisos para acceder a esta función.')
        return HttpResponseForbidden("No tienes permisos para acceder a esta función.")
    
    orden = get_object_or_404(OrdenDeTrabajo, id=orden_id)
    
    if request.method == 'POST':
        form = AsignacionYEstadoForm(request.POST, instance=orden)
        if form.is_valid():
            try:
                orden_actualizada = form.save()
                
                # Si se cierra la orden, establecer fecha de cierre si no está establecida
                if orden_actualizada.estado == 'Cerrada' and not orden_actualizada.fecha_cierre_real:
                    orden_actualizada.fecha_cierre_real = timezone.now()
                    orden_actualizada.save()
                
                # Guardar en sesión la última orden modificada
                request.session['ultima_orden_vista'] = orden_id
                
                messages.success(request, 
                    f'✅ Orden #{orden_id} actualizada exitosamente! '
                    f'Estado: {orden_actualizada.estado}'
                )
                return redirect('gestion_mantenimiento:lista_ordenes')  # CORREGIDO
                
            except Exception as e:
                messages.error(request, f'❌ Error al actualizar la orden: {str(e)}')
        else:
            messages.error(request, '❌ Por favor corrige los errores en el formulario.')
    else:
        form = AsignacionYEstadoForm(instance=orden)
    
    context = {
        'form': form, 
        'orden': orden,
        'titulo_pagina': f'Asignar/Editar Orden #{orden_id}'
    }
    return render(request, 'gestion_mantenimiento/asignar_orden.html', context)

# =============================================================================
# VISTA PARA ELIMINAR ÓRDENES (SOLO ADMINISTRADOR)
# =============================================================================

@login_required
@permission_required('gestion_mantenimiento.delete_ordendetrabajo', raise_exception=True)
def eliminar_orden(request, orden_id):
    """
    Vista para eliminar órdenes (solo usuarios con permiso delete_ordendetrabajo)
    """
    orden = get_object_or_404(OrdenDeTrabajo, id=orden_id)
    
    if request.method == 'POST':
        try:
            orden_titulo = orden.titulo
            orden_id = orden.id
            orden.delete()
            
            messages.success(request, 
                f'✅ Orden #{orden_id} "{orden_titulo}" eliminada exitosamente.'
            )
            return redirect('gestion_mantenimiento:lista_ordenes')  # CORREGIDO
            
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar la orden: {str(e)}')
    
    context = {
        'orden': orden,
        'titulo_pagina': f'Eliminar Orden #{orden_id}'
    }
    return render(request, 'gestion_mantenimiento/eliminar_orden.html', context)

# =============================================================================
# VISTAS ADICIONALES - DETALLE DE ORDEN
# =============================================================================

@login_required
def detalle_orden(request, orden_id):
    """
    Vista para ver el detalle de una orden específica
    """
    orden = get_object_or_404(OrdenDeTrabajo, id=orden_id)
    
    # Verificar permisos para ver esta orden
    if (request.user.groups.filter(name='Operario').exists() and 
        orden.operario_creador != request.user and 
        orden.operario_asignado != request.user):
        messages.error(request, '❌ No tienes permisos para ver esta orden.')
        return HttpResponseForbidden("No tienes permisos para ver esta orden.")
    
    # Guardar en sesión la última orden vista
    request.session['ultima_orden_vista'] = orden_id
    
    # Obtener consumos relacionados
    consumos = orden.consumos.all().select_related('suministro')
    
    context = {
        'orden': orden,
        'consumos': consumos,
        'titulo_pagina': f'Detalle Orden #{orden_id}'
    }
    return render(request, 'gestion_mantenimiento/detalle_orden.html', context)

# =============================================================================
# VISTA DE INICIO / DASHBOARD
# =============================================================================

@login_required
def dashboard(request):
    """
    Vista de dashboard con estadísticas
    """
    # Estadísticas básicas
    total_ordenes = OrdenDeTrabajo.objects.count()
    ordenes_pendientes = OrdenDeTrabajo.objects.filter(estado='Pendiente').count()
    ordenes_en_progreso = OrdenDeTrabajo.objects.filter(estado='En Progreso').count()
    
    # Estadísticas por usuario
    if request.user.groups.filter(name='Operario').exists():
        mis_ordenes = OrdenDeTrabajo.objects.filter(
            models.Q(operario_creador=request.user) | 
            models.Q(operario_asignado=request.user)
        ).count()
        mis_pendientes = OrdenDeTrabajo.objects.filter(
            operario_asignado=request.user,
            estado='Pendiente'
        ).count()
    else:
        mis_ordenes = None
        mis_pendientes = None
    
    context = {
        'total_ordenes': total_ordenes,
        'ordenes_pendientes': ordenes_pendientes,
        'ordenes_en_progreso': ordenes_en_progreso,
        'mis_ordenes': mis_ordenes,
        'mis_pendientes': mis_pendientes,
        'titulo_pagina': 'Dashboard'
    }
    return render(request, 'gestion_mantenimiento/dashboard.html', context)
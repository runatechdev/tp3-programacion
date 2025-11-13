# 📋 ESPECIFICACIONES TÉCNICAS - MantenimientoFlow

## Documento de Análisis Técnico
**Tecnicatura Superior en Desarrollo de Software - Programación VI**

---

## 1. REQUISITOS CUMPLIDOS

### ✅ 1.1 Autenticación
- [x] Login personalizado con usuario y contraseña
- [x] Logout con cierre de sesión
- [x] Redirección a login si no está autenticado
- [x] Mensajes de error/éxito

**Archivos:** `views.py` (login_view, logout_view)

### ✅ 1.2 Sesiones
- [x] Guardar última orden visualizada en sesión
- [x] Acceso rápido al regresar
- [x] Timeout de 15 minutos de inactividad
- [x] Mensajes personalizados

**Archivos:** 
- `views.py` (request.session)
- `middleware.py` (SessionTimeoutMiddleware)
- `settings.py` (SESSION_COOKIE_AGE = 900)

### ✅ 1.3 Autorización y Permisos
- [x] Tres grupos: Operario, Jefe de Taller, Administrador
- [x] Operario solo ve sus órdenes (creadas/asignadas)
- [x] Botón Eliminar solo visible para Administrador
- [x] Vistas protegidas con decoradores

**Archivos:** 
- `views.py` (decoradores @user_passes_test, @permission_required)
- `templates/` (condicionales {{perms}}, {{user.groups}})

### ✅ 1.4 ORM y Consultas
- [x] Modelar entidades principales
- [x] Relaciones ForeignKey y OneToMany
- [x] Filtrados con Q objects
- [x] Select_related para optimizar

**Archivos:** `models.py` (OrdenDeTrabajo, Suministro, ConsumoSuministro)

---

## 2. MODELOS PRINCIPALES

### 2.1 OrdenDeTrabajo

```python
class OrdenDeTrabajo(models.Model):
    ESTADOS = [('Pendiente', 'Pendiente'), ('En Progreso', 'En Progreso'), ('Cerrada', 'Cerrada')]
    PRIORIDADES = [('Baja', 'Baja'), ('Media', 'Media'), ('Alta', 'Alta')]
    
    Fields:
    ├── titulo: CharField(max_length=200)
    ├── fecha: DateField() ✅ NUEVO
    ├── fecha_creacion: DateTimeField(auto_now_add=True)
    ├── descripcion_falla: TextField()
    ├── prioridad: CharField(choices=PRIORIDADES)
    ├── estado: CharField(choices=ESTADOS)
    ├── operario_creador: ForeignKey(User, related_name='ordenes_creadas')
    ├── operario_asignado: ForeignKey(User, related_name='ordenes_asignadas', null=True, blank=True)
    └── fecha_cierre_real: DateTimeField(null=True, blank=True)
    
    Meta:
    ├── ordering = ['-fecha_creacion']
    ├── verbose_name = "Orden de Trabajo"
    └── permissions = [("can_close_order", "Puede cerrar órdenes")]
    
    Methods:
    ├── __str__() → "OT-{id}: {titulo} - {estado}"
    ├── get_absolute_url() → reverse('detalle_orden', kwargs={'pk': self.pk})
    ├── @property esta_cerrada
    └── @property puede_consumir_suministros
```

**Relaciones:**
```
OrdenDeTrabajo (1) ←→ (N) ConsumoSuministro (cascade delete)
    ├─ operario_creador → User
    └─ operario_asignado → User (nullable)
```

### 2.2 Suministro

```python
class Suministro(models.Model):
    Fields:
    ├── nombre: CharField(max_length=100)
    ├── descripcion: TextField()
    ├── stock: PositiveIntegerField(default=0)
    ├── precio_unitario: DecimalField(max_digits=10, decimal_places=2)
    └── fecha_actualizacion: DateTimeField(auto_now=True)
    
    Meta:
    ├── ordering = ['nombre']
    └── verbose_name_plural = "Suministros"
    
    Methods:
    ├── __str__() → "{nombre} (Stock: {stock})"
    ├── @property stock_bajo → stock < 10
    ├── reducir_stock(cantidad) → Bool
    └── aumentar_stock(cantidad) → Bool
```

**Relaciones:**
```
Suministro (1) ←→ (N) ConsumoSuministro (cascade delete)
```

### 2.3 ConsumoSuministro

```python
class ConsumoSuministro(models.Model):
    Fields:
    ├── orden_de_trabajo: ForeignKey(OrdenDeTrabajo, related_name='consumos')
    ├── suministro: ForeignKey(Suministro, related_name='consumos')
    ├── cantidad_usada: PositiveIntegerField()
    ├── fecha_consumo: DateTimeField(auto_now_add=True)
    └── operario_registra: ForeignKey(User, related_name='consumos_registrados')
    
    Meta:
    ├── ordering = ['-fecha_consumo']
    └── unique_together = [('orden_de_trabajo', 'suministro')]
    
    Methods:
    ├── __str__() → "{cantidad_usada} x {suministro.nombre}"
    ├── save() → Actualiza stock automáticamente
    └── @property costo_total → cantidad_usada * precio_unitario
```

**Comportamiento en save():**
- Al crear nuevo ConsumoSuministro, automáticamente reduce stock del Suministro

---

## 3. FORMULARIOS Y VALIDACIONES

### 3.1 Formulario 1: OrdenDeTrabajoForm

**Purpose:** Crear nuevas órdenes (reportar fallas)
**Usuarios:** Operarios
**Campos:**
```python
[
    'titulo',
    'fecha',           # ✅ NUEVO CAMPO
    'descripcion_falla',
    'prioridad'
]
```

**Validaciones Nivel Campo:**
1. **clean_descripcion_falla()**
   ```
   ✓ min_length = 20 caracteres
   ✓ Error si < 20 caracteres
   ```

2. **clean_fecha()** ✅ NUEVO
   ```
   ✓ Debe ser fecha actual o posterior
   ✓ Error si fecha < hoy
   ```

**Validaciones Nivel Formulario (clean()):**
1. **Para prioridad "Alta":**
   ```
   ✓ Descripción debe contener palabras clave:
     - "detenido", "bloqueado", "fuego"
     - "urgente", "crítico", "emergencia"
     - "parado", "inoperativo", "falla total"
   ✓ Error si Alta sin palabras clave
   ```

**Widgets:** Form Control (Bootstrap)

---

### 3.2 Formulario 2: ConsumoSuministroForm

**Purpose:** Registrar consumo de suministros
**Usuarios:** Operarios
**Campos:**
```python
[
    'orden_de_trabajo',  # Filtrada: solo abiertas del usuario
    'suministro',        # Filtrada: solo con stock > 0
    'cantidad_usada'
]
```

**Validaciones Nivel Campo:**
1. **clean_cantidad_usada()**
   ```
   ✓ cantidad > 0
   ```

**Validaciones Nivel Formulario (clean()):**
1. **CRÍTICA - Verificar Stock:**
   ```python
   if cantidad_usada > suministro.stock:
       raise ValidationError("Stock insuficiente")
   ```

2. **Fecha posterior a orden:**
   ```python
   if timezone.now() < orden.fecha_creacion:
       raise ValidationError("No se puede consumir antes de crear orden")
   ```

**Actualización de Stock:**
- Automática en modelo ConsumoSuministro.save()
- No requiere lógica adicional en vista

**Filtrado de QuerySet:**
```python
# Órdenes disponibles
orden_de_trabajo.queryset = OrdenDeTrabajo.objects.filter(
    estado__in=['Pendiente', 'En Progreso'],
    operario_asignado=user
)

# Suministros disponibles
suministro.queryset = Suministro.objects.filter(stock__gt=0)
```

---

### 3.3 Formulario 3: AsignacionYEstadoForm

**Purpose:** Asignar órdenes y cambiar estado
**Usuarios:** Jefes de Taller
**Campos:**
```python
[
    'operario_asignado',  # Filtrada: solo grupo Operario
    'estado',
    'fecha_cierre_real'
]
```

**Validaciones Nivel Campo:**
1. **clean_fecha_cierre_real()**
   ```
   ✓ No puede ser futura
   ✓ Error si fecha > hoy
   ```

**Validaciones Nivel Formulario (clean()):**
1. **Condicional - Estado Cerrada:**
   ```python
   if estado == 'Cerrada' and not fecha_cierre_real:
       raise ValidationError("fecha_cierre_real obligatoria para Cerrada")
   ```

2. **Fecha posterior a creación:**
   ```python
   if fecha_cierre_real < fecha_creacion:
       raise ValidationError("No puede ser anterior a creación")
   ```

**Filtrado de QuerySet:**
```python
# Solo operarios
operario_asignado.queryset = User.objects.filter(groups__name='Operario')
```

---

## 4. VISTAS

### 4.1 Login/Logout

**login_view(request)**
- Método: POST/GET
- No requiere @login_required
- Redirige si ya está autenticado
- Mensaje de bienvenida personalizado

**logout_view(request)**
- Método: GET/POST
- @login_required
- Destruye sesión
- Redirige a login

### 4.2 Lista de Órdenes (Principal)

**lista_ordenes(request)**
- @login_required
- Filtra por rol:
  ```
  Operario → solo sus órdenes (creadas O asignadas)
  Jefe → todas las órdenes
  Admin → todas las órdenes
  ```
- Filtro por estado con GET param
- Guarda última orden en sesión
- Context con rol_usuario, estado_filtro

**ORM Queries:**
```python
# Operario
OrdenDeTrabajo.objects.filter(
    Q(operario_creador=user) | Q(operario_asignado=user)
).order_by('-fecha_creacion')

# Con filtro estado
.filter(estado=estado_filtro)
```

### 4.3 Crear Orden

**crear_orden(request)**
- @login_required
- @user_passes_test(lambda u: u.groups.filter(name='Operario').exists())
- Asocia operario_creador = request.user
- Guarda en sesión última orden creada
- Mensajes de éxito/error

### 4.4 Consumo de Suministro

**consumo_suministro(request)**
- @login_required
- @user_passes_test(Operario)
- Form recibe user como parámetro
- Filtra órdenes: estado Pendiente/En Progreso + asignadas a user
- Actualiza stock automáticamente
- Mensajes con cantidad y stock restante

### 4.5 Asignación y Estado

**asignar_orden(request, orden_id)**
- @login_required
- Verifica user en grupo "Jefe de Taller"
- Si estado="Cerrada" sin fecha_cierre_real, setea timezone.now()
- Guarda en sesión última orden modificada

### 4.6 Eliminar Orden

**eliminar_orden(request, orden_id)**
- @login_required
- @permission_required('delete_ordendetrabajo', raise_exception=True)
- Método POST para confirmar eliminación
- Solo disponible para Admin

### 4.7 Detalle Orden

**detalle_orden(request, orden_id)**
- @login_required
- Verifica permisos para ver orden
- Operario solo ve sus órdenes
- Obtiene consumos relacionados
- Guarda en sesión última orden vista

---

## 5. PERMISOS POR GRUPO

### 5.1 Asignación de Permisos

```python
# OPERARIO
├── add_ordendetrabajo ✓
└── add_consumosuministro ✓

# JEFE DE TALLER
├── add_ordendetrabajo ✓
├── change_ordendetrabajo ✓
├── view_ordendetrabajo ✓
├── add_suministro ✓
├── change_suministro ✓
├── delete_suministro ✓
├── add_consumosuministro ✓
└── is_staff = True

# ADMINISTRADOR
├── Todos los permisos ✓
├── is_staff = True
└── is_superuser = True
```

### 5.2 Decoradores Usados

```python
@login_required
  → Redirige a /login/ si no autenticado

@user_passes_test(lambda u: u.groups.filter(name='Operario').exists())
  → Verifica grupo, redirige a /login/ si no cumple

@permission_required('app.permission_name', raise_exception=True)
  → HttpResponseForbidden 403 si no tiene permiso
```

---

## 6. MIDDLEWARE PERSONALIZADO

### SessionTimeoutMiddleware

**Ubicación:** `gestion_mantenimiento/middleware.py`

**Funcionalidad:**
```python
class SessionTimeoutMiddleware:
    - Calcula tiempo desde último acceso
    - Si > 900 segundos (15 minutos):
        • Hace logout automático
        • Muestra mensaje de advertencia
        • Redirige a /login/
    - Actualiza timestamp de último acceso
```

**Configuración en settings.py:**
```python
MIDDLEWARE = [
    ...
    'gestion_mantenimiento.middleware.SessionTimeoutMiddleware',
]

SESSION_COOKIE_AGE = 900
SESSION_SAVE_EVERY_REQUEST = True
```

---

## 7. ESTRUCTURA DE DIRECTORIOS

```
mantenimiento_flow_project/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md ✅ NUEVO
├── ESPECIFICACIONES_TECNICAS.md ✅ NUEVO
│
├── mantenimiento_flow/
│   ├── settings.py ✅ MODIFICADO (middleware)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── gestion_mantenimiento/
    ├── models.py ✅ MODIFICADO (campo fecha)
    ├── forms.py ✅ MODIFICADO (validaciones fecha)
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── middleware.py ✅ NUEVO
    ├── apps.py
    │
    ├── management/
    │   └── commands/
    │       └── crear_datos_prueba.py ✅ COMPLETO
    │
    ├── migrations/
    │   └── (archivos de migración)
    │
    ├── templates/gestion_mantenimiento/
    │   ├── base.html
    │   ├── login.html
    │   ├── lista_ordenes.html
    │   ├── crear_orden.html
    │   ├── detalle_orden.html
    │   ├── asignar_orden.html
    │   ├── consumo_suministro.html
    │   └── eliminar_orden.html
    │
    └── static/
        ├── css/
        ├── js/
        └── images/
```

---

## 8. FLUJO DE DATOS

### 8.1 Crear Orden

```
Usuario (Operario)
    ↓
GET /crear-orden/
    ↓
Vista: crear_orden(request)
    ↓
Form: OrdenDeTrabajoForm()
    ↓
Validaciones:
    • descripcion_falla >= 20 chars
    • fecha >= hoy
    • Si Alta: keywords en descripción
    ↓
POST /crear-orden/ + datos
    ↓
form.is_valid() ?
    ├─ YES → orden.save() + operario_creador=request.user
    │        → session['ultima_orden_vista'] = orden.id
    │        → redirect lista_ordenes
    │        → mensaje SUCCESS
    │
    └─ NO → re-render form + field errors
```

### 8.2 Registrar Consumo

```
Usuario (Operario)
    ↓
GET /consumo-suministro/
    ↓
Vista: consumo_suministro(request)
    ↓
Form: ConsumoSuministroForm(request.user)
    ├─ orden_de_trabajo.queryset = órdenes abiertas del user
    └─ suministro.queryset = suministros con stock > 0
    ↓
POST /consumo-suministro/ + datos
    ↓
Validaciones:
    • cantidad > 0
    • cantidad <= suministro.stock ✓ CRÍTICA
    • fecha >= fecha_creacion orden
    ↓
consumo.save()
    ↓
ConsumoSuministro.save() override:
    ├─ suministro.reducir_stock(cantidad)
    └─ super().save()
    ↓
redirect lista_ordenes + SUCCESS
```

### 8.3 Asignar Orden

```
Usuario (Jefe de Taller)
    ↓
GET /orden/<id>/asignar/
    ↓
Verificar: user.groups = "Jefe de Taller"
    ├─ NO → HttpResponseForbidden 403
    └─ YES → continuar
    ↓
Vista: asignar_orden(request, orden_id)
    ↓
Form: AsignacionYEstadoForm(instance=orden)
    ├─ operario_asignado.queryset = User.filter(groups__name='Operario')
    └─ fecha_cierre_real.required = False (por ahora)
    ↓
POST /orden/<id>/asignar/ + datos
    ↓
Validaciones:
    • Si estado="Cerrada" → fecha_cierre_real obligatorio
    • fecha_cierre_real <= hoy
    • fecha_cierre_real > fecha_creacion
    ↓
form.is_valid() ?
    ├─ YES → orden.save()
    │        → Si estado=Cerrada sin fecha_cierre_real
    │        │  → orden.fecha_cierre_real = timezone.now()
    │        → session['ultima_orden_vista'] = orden_id
    │        → SUCCESS
    │
    └─ NO → re-render + errors
```

---

## 9. QUERYS OPTIMIZADAS

### 9.1 Lista de órdenes (Operario)

```python
# INEFFICIENT ❌
ordenes = OrdenDeTrabajo.objects.filter(
    Q(operario_creador=user) | Q(operario_asignado=user)
)
for orden in ordenes:
    print(orden.operario_creador.username)  # N queries

# OPTIMIZED ✓
ordenes = OrdenDeTrabajo.objects.filter(
    Q(operario_creador=user) | Q(operario_asignado=user)
).select_related('operario_creador', 'operario_asignado')
```

### 9.2 Detalle orden con consumos

```python
consumos = orden.consumos.all().select_related('suministro', 'operario_registra')
```

---

## 10. SEGURIDAD

### 10.1 CSRF Protection
- {% csrf_token %} en todos los formularios
- Configurado en settings.py

### 10.2 SQL Injection
- Uso de ORM (QuerySet)
- Parámetros con ? bindings

### 10.3 XSS Protection
- Template escaping automático
- {{ variable }} → escapado
- {{ variable|safe }} → solo donde necesario

### 10.4 Autenticación
- Sesiones de Django
- SessionMiddleware
- Authentication middleware

### 10.5 Autorización
- Decoradores @login_required
- Group checking
- Permission checking

---

## 11. PRUEBAS Y DATOS DE PRUEBA

### 11.1 Comando crear_datos_prueba

```bash
python manage.py crear_datos_prueba
```

**Crea automáticamente:**
- 3 grupos con permisos configurados
- 1 admin + 2 jefes + 4 operarios
- 10+ suministros con stock
- 6 órdenes de ejemplo
- Consumos registrados

---

## 12. MEJORAS FUTURAS

- [ ] API REST con Django REST Framework
- [ ] Reportes en PDF
- [ ] Gráficos de productividad
- [ ] Email notifications
- [ ] Sistema de tareas automáticas (Celery)
- [ ] WebSocket para notificaciones en tiempo real
- [ ] Tests unitarios completos
- [ ] Integración con ERP

---

**Documento generado:** 13 de Noviembre de 2025
**Versión:** 1.0
**Estado:** Completo ✓

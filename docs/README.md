# 🔧 MantenimientoFlow - Sistema de Gestión de Mantenimiento

**Tecnicatura Superior en Desarrollo de Software - Programación VI**

Un sistema web completo desarrollado en Django para gestionar órdenes de trabajo y control de inventario de suministros en ambientes empresariales.

## 📋 Índice

- [Características principales](#características-principales)
- [Requisitos del sistema](#requisitos-del-sistema)
- [Instalación y configuración](#instalación-y-configuración)
- [Uso del sistema](#uso-del-sistema)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Roles y permisos](#roles-y-permisos)
- [Validaciones implementadas](#validaciones-implementadas)
- [Base de datos](#base-de-datos)

## ✨ Características principales

### 1. **Sistema de Autenticación y Autorización**
- Login/Logout con sesiones seguras
- Timeout automático de 15 minutos de inactividad
- Tres roles de usuario con permisos específicos:
  - 👔 **Operarios**: Crear órdenes y registrar consumos
  - 👨‍💼 **Jefes de Taller**: Asignar órdenes, gestionar estados e inventario
  - 👑 **Administradores**: Control total del sistema

### 2. **Gestión de Órdenes de Trabajo**
- Crear nuevas órdenes (reportar fallas)
- Asignar operarios a órdenes
- Cambiar estado de órdenes (Pendiente → En Progreso → Cerrada)
- Visualizar historial y detalles de órdenes
- Control de acceso basado en rol

### 3. **Control de Inventario**
- Registro de suministros disponibles
- Actualización automática de stock al registrar consumos
- Validación de stock disponible antes de consumir
- Alertas de stock bajo

### 4. **Sistema de Sesiones**
- Guardar última orden visualizada para acceso rápido
- Mensajes personalizados de éxito/error
- Timeout de 15 minutos de inactividad

## 🛠️ Requisitos del sistema

- Python 3.8+
- Django 5.2.8
- Entorno virtual (recomendado)

## 📦 Instalación y configuración

### 1. Clonar/Descargar el proyecto

```bash
cd mantenimiento_flow_project
```

### 2. Crear y activar entorno virtual

```bash
# En Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# En Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear datos de prueba (IMPORTANTE)

```bash
python manage.py crear_datos_prueba
```

Este comando crea:
- **3 Grupos**: Operario, Jefe de Taller, Administrador
- **1 Superusuario (Admin)**:
  - Usuario: `admin`
  - Contraseña: `admin123`
  
- **2 Jefes de Taller**:
  - Usuario: `jefe1` / Contraseña: `jefe123`
  - Usuario: `jefe2` / Contraseña: `jefe123`

- **4 Operarios**:
  - Usuario: `operario1` / Contraseña: `oper123`
  - Usuario: `operario2` / Contraseña: `oper123`
  - Usuario: `operario3` / Contraseña: `oper123`
  - Usuario: `operario4` / Contraseña: `oper123`

- **10+ Suministros** precargados en inventario
- **6 Órdenes de trabajo** de ejemplo
- **Consumos** registrados para demostración

### 6. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

Acceder a: `http://127.0.0.1:8000/login/`

## 🎯 Uso del sistema

### Flujo de trabajo principal

#### 1️⃣ Reporte de Falla (Operario)
- El operario accede al sistema
- Navega a **"Crear Nueva Orden de Trabajo"**
- Completa el formulario:
  - **Título**: Breve descripción
  - **Fecha de Reporte**: Fecha actual o futura
  - **Descripción**: Mínimo 20 caracteres
  - **Prioridad**: Baja, Media o Alta
- Si prioridad es **Alta**, debe incluir palabras de urgencia
- Submit → Orden creada en estado "Pendiente"

#### 2️⃣ Asignación y Planificación (Jefe de Taller)
- Jefe visualiza todas las órdenes
- Selecciona una orden → **"Asignar/Editar"**
- Asigna un operario (puede ser el mismo que reportó)
- Cambia estado si es necesario
- Guarda cambios

#### 3️⃣ Ejecución y Consumo (Operario)
- Operario en estado "En Progreso" visualiza sus órdenes asignadas
- Va a **"Registrar Consumo de Suministro"**
- Selecciona:
  - **Orden de Trabajo**: De sus órdenes abiertas
  - **Suministro**: Material utilizado
  - **Cantidad**: Cantidad consumida
- Sistema valida stock disponible
- Stock se actualiza automáticamente

#### 4️⃣ Cierre y Verificación (Jefe de Taller)
- Jefe revisa orden completada
- Cambia estado a **"Cerrada"**
- Registra **fecha real de cierre**
- Orden finaliza y se registra en historial

## 👥 Roles y permisos

### Operario
| Acción | Permiso |
|--------|---------|
| Crear órdenes de trabajo | ✅ |
| Ver solo sus órdenes (creadas/asignadas) | ✅ |
| Registrar consumo de suministros | ✅ |
| Editar/Asignar órdenes | ❌ |
| Eliminar órdenes | ❌ |
| Acceso a panel de admin | ❌ |

### Jefe de Taller
| Acción | Permiso |
|--------|---------|
| Ver todas las órdenes | ✅ |
| Asignar órdenes a operarios | ✅ |
| Cambiar estado de órdenes | ✅ |
| Gestionar inventario (suministros) | ✅ |
| Eliminar órdenes | ❌ |
| Acceso a panel de admin | ✅ |

### Administrador
| Acción | Permiso |
|--------|---------|
| Todas las acciones | ✅ |
| Gestión de usuarios | ✅ |
| Panel de admin completo | ✅ |
| Eliminar órdenes | ✅ |

## ✔️ Validaciones implementadas

### Formulario 1: OrdenDeTrabajoForm

**Validaciones a nivel de campo:**
- `descripcion_falla`: Mínimo 20 caracteres
- `fecha`: Debe ser la fecha actual o futura
- `prioridad`: Campo requerido

**Validaciones a nivel de formulario:**
- Si prioridad es **"Alta"**, la descripción debe contener palabras clave:
  - "detenido", "bloqueado", "fuego", "urgente", "crítico", "emergencia", etc.

### Formulario 2: ConsumoSuministroForm

**Validaciones a nivel de campo:**
- `cantidad_usada`: Debe ser mayor a 0

**Validaciones a nivel de formulario:**
- ✅ **CRÍTICA**: `cantidad_usada` no puede exceder stock disponible del suministro
- Fecha de consumo debe ser posterior a fecha de creación de orden
- Stock se actualiza automáticamente al guardar

### Formulario 3: AsignacionYEstadoForm

**Validaciones a nivel de campo:**
- `fecha_cierre_real`: No puede ser futura

**Validaciones a nivel de formulario:**
- **Condicional**: Si estado es "Cerrada", `fecha_cierre_real` es obligatorio
- `fecha_cierre_real` debe ser posterior a `fecha_creacion` de la orden

## 💾 Base de datos

### Modelos principales

#### OrdenDeTrabajo
```python
- id (PK)
- titulo (CharField, max_length=200)
- fecha (DateField) - Fecha de reporte
- fecha_creacion (DateTimeField, auto_now_add=True)
- descripcion_falla (TextField)
- prioridad (CharField, choices=[Baja, Media, Alta])
- estado (CharField, choices=[Pendiente, En Progreso, Cerrada])
- operario_creador (FK → User)
- operario_asignado (FK → User, nullable)
- fecha_cierre_real (DateTimeField, nullable)
```

#### Suministro
```python
- id (PK)
- nombre (CharField, max_length=100)
- descripcion (TextField)
- stock (PositiveIntegerField)
- precio_unitario (DecimalField)
- fecha_actualizacion (DateTimeField, auto_now=True)
```

#### ConsumoSuministro
```python
- id (PK)
- orden_de_trabajo (FK → OrdenDeTrabajo)
- suministro (FK → Suministro)
- cantidad_usada (PositiveIntegerField)
- fecha_consumo (DateTimeField, auto_now_add=True)
- operario_registra (FK → User)
- unique_together: (orden_de_trabajo, suministro)
```

### Relaciones importantes

```
OrdenDeTrabajo (1) ──────→ (N) ConsumoSuministro
    ↓
    ├─→ operario_creador (User)
    └─→ operario_asignado (User)

Suministro (1) ──────→ (N) ConsumoSuministro
```

## 🔐 Seguridad

### Autenticación
- Login requerido para acceder a cualquier función
- Sesiones seguras con CSRF protection

### Autorización
- Decoradores `@login_required`
- Decoradores `@permission_required`
- Decoradores `@user_passes_test` para verificar grupo
- Filtrado de queryset por usuario

### Sesiones
- Timeout automático: 15 minutos de inactividad
- SESSION_COOKIE_AGE = 900 segundos
- SESSION_SAVE_EVERY_REQUEST = True
- Middleware personalizado para validar inactividad

## 📊 Panel de Administración

Acceder a: `http://127.0.0.1:8000/admin/`

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

**Funcionalidades:**
- Gestión completa de usuarios y grupos
- Edición de órdenes de trabajo
- Control de inventario de suministros
- Visualización de consumos registrados
- Filtros y búsquedas avanzadas

## 📱 Interfaz de usuario

### Navegación principal
```
Home (Lista de Órdenes)
├── Crear Nueva Orden (solo Operarios)
├── Ver Detalle (todos)
├── Asignar/Editar (Jefes y Admin)
├── Eliminar (solo Admin)
└── Registrar Consumo (solo Operarios)
```

### Características UI
- Diseño responsive
- Mensajes flash personalizados
- Acceso rápido a última orden visualizada
- Filtros por estado
- Indicadores visuales (badges, colores)
- Iconos para mejor UX

## 🐛 Troubleshooting

### Problema: "Módulo django no encontrado"
**Solución:**
```bash
source .venv/bin/activate  # Activar entorno virtual
pip install Django==5.2.8
```

### Problema: "Error en migraciones"
**Solución:**
```bash
python manage.py migrate --run-syncdb
```

### Problema: "No aparecen usuarios de prueba"
**Solución:**
```bash
python manage.py crear_datos_prueba
```

### Problema: "Sesión expira demasiado rápido"
Revisar `mantenimiento_flow/settings.py`:
```python
SESSION_COOKIE_AGE = 900  # 15 minutos
SESSION_SAVE_EVERY_REQUEST = True
```

## 📞 Soporte

Para reportar bugs o sugerencias, contactar con el desarrollador.

## 📄 Licencia

Proyecto académico - Tecnicatura Superior en Desarrollo de Software

---

**Última actualización:** 13 de Noviembre de 2025

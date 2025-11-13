# ⚡ REFERENCIA RÁPIDA - MantenimientoFlow

**Guía de consulta rápida para desarrolladores**

---

## 🚀 INICIO RÁPIDO

```bash
# Activar entorno
source .venv/bin/activate

# Crear datos de prueba
python manage.py crear_datos_prueba

# Ejecutar servidor
python manage.py runserver

# Acceder
http://127.0.0.1:8000/login/
```

---

## 👥 CREDENCIALES DE PRUEBA

```
Admin:     admin / admin123
Jefe 1:    jefe1 / jefe123
Jefe 2:    jefe2 / jefe123
Operario1: operario1 / oper123
Operario2: operario2 / oper123
Operario3: operario3 / oper123
Operario4: operario4 / oper123
```

---

## 🗺️ RUTAS PRINCIPALES

| Ruta | Descripción | Quién |
|------|-----------|-------|
| `/login/` | Iniciar sesión | Todos |
| `/logout/` | Cerrar sesión | Autenticado |
| `/` | Lista de órdenes | Autenticado |
| `/crear-orden/` | Crear orden | Operario |
| `/orden/<id>/` | Ver detalle | Creador/Asignado |
| `/orden/<id>/asignar/` | Asignar orden | Jefe/Admin |
| `/orden/<id>/eliminar/` | Eliminar orden | Admin |
| `/consumo-suministro/` | Registrar consumo | Operario |
| `/admin/` | Panel administración | Staff |

---

## 📋 MODELOS

### OrdenDeTrabajo
```python
- titulo (str)
- fecha (date)
- fecha_creacion (datetime, auto)
- descripcion_falla (text)
- prioridad (choice: Baja/Media/Alta)
- estado (choice: Pendiente/En Progreso/Cerrada)
- operario_creador (User FK)
- operario_asignado (User FK, nullable)
- fecha_cierre_real (datetime, nullable)
```

### Suministro
```python
- nombre (str)
- descripcion (text)
- stock (int)
- precio_unitario (decimal)
- fecha_actualizacion (datetime, auto)
```

### ConsumoSuministro
```python
- orden_de_trabajo (FK)
- suministro (FK)
- cantidad_usada (int)
- fecha_consumo (datetime, auto)
- operario_registra (User FK)
```

---

## 📝 VALIDACIONES CLAVE

### OrdenDeTrabajoForm
```
- descripcion_falla >= 20 caracteres
- fecha >= hoy
- Si prioridad=Alta: palabras clave en descripción
  (detenido, bloqueado, fuego, urgente, crítico)
```

### ConsumoSuministroForm
```
- cantidad > 0
- cantidad <= suministro.stock ⭐ CRÍTICA
- fecha >= fecha_creacion orden
- Stock se actualiza automáticamente
```

### AsignacionYEstadoForm
```
- Si estado=Cerrada: fecha_cierre_real obligatoria
- fecha_cierre_real <= hoy
- fecha_cierre_real > fecha_creacion
- operario_asignado: solo del grupo Operario
```

---

## 🔐 PERMISOS POR GRUPO

```
OPERARIO
├─ add_ordendetrabajo
├─ add_consumosuministro
└─ is_staff = False

JEFE DE TALLER
├─ add_ordendetrabajo
├─ change_ordendetrabajo
├─ view_ordendetrabajo
├─ add_suministro
├─ change_suministro
├─ delete_suministro
├─ add_consumosuministro
└─ is_staff = True

ADMINISTRADOR
├─ Todos los permisos
├─ is_staff = True
└─ is_superuser = True
```

---

## 🎯 FLUJO DE TRABAJO

```
1. Operario crea orden → Estado: Pendiente
2. Jefe asigna operario → Estado: En Progreso
3. Operario registra consumos → Stock ↓ automático
4. Jefe cierra orden → Estado: Cerrada, fecha_cierre_real
```

---

## 📊 CONFIGURACIÓN IMPORTANTE

```python
# settings.py

# Sesiones
SESSION_COOKIE_AGE = 900  # 15 minutos
SESSION_SAVE_EVERY_REQUEST = True

# Idioma
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'

# Middleware personalizado
'gestion_mantenimiento.middleware.SessionTimeoutMiddleware'
```

---

## 🛠️ COMANDOS ÚTILES

```bash
# Crear datos de prueba
python manage.py crear_datos_prueba

# Crear superuser
python manage.py createsuperuser

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Shell Django
python manage.py shell

# Ver usuarios
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.all()

# Limpiar base de datos
python manage.py flush
```

---

## 📋 ESTRUCTURA ARCHIVOS CLAVE

```
gestion_mantenimiento/
├── models.py          # 3 modelos principales
├── forms.py           # 3 formularios con validaciones
├── views.py           # 8 vistas principales
├── middleware.py      # Timeout de sesión
├── admin.py           # Panel admin personalizado
├── urls.py            # Rutas de la app
│
├── management/
│   └── commands/
│       └── crear_datos_prueba.py
│
└── templates/
    └── gestion_mantenimiento/
        ├── base.html
        ├── login.html
        ├── lista_ordenes.html
        ├── crear_orden.html
        ├── detalle_orden.html
        ├── asignar_orden.html
        ├── consumo_suministro.html
        └── eliminar_orden.html
```

---

## 🐛 PROBLEMAS COMUNES

**Problema:** "ModuleNotFoundError: No module named 'django'"
```bash
source .venv/bin/activate
pip install Django==5.2.8
```

**Problema:** "Sesión no expira después de 15 minutos"
```python
# settings.py
SESSION_COOKIE_AGE = 900
SESSION_SAVE_EVERY_REQUEST = True
# En middleware.py: verificar que esté en MIDDLEWARE
```

**Problema:** "No aparecen datos de prueba"
```bash
python manage.py crear_datos_prueba
```

**Problema:** "No puedo acceder a admin"
```bash
# Crear superuser
python manage.py createsuperuser
# O usar admin/admin123 si ya existe
```

---

## ✅ CHECKLIST PRE-ENTREGA

- [ ] Servidor ejecutándose sin errores
- [ ] `python manage.py check` sin problemas
- [ ] Datos de prueba creados
- [ ] Login funcional (probar 3 roles)
- [ ] Crear orden: validaciones funcionan
- [ ] Registrar consumo: stock se actualiza
- [ ] Asignar orden: solo Jefes
- [ ] Eliminar orden: solo Admin visible
- [ ] Timeout de sesión: 15 minutos
- [ ] Documentación presente (README, specs)
- [ ] Panel admin accesible

---

## 📚 DOCUMENTOS INCLUIDOS

1. **README.md** - Guía de usuario
2. **ESPECIFICACIONES_TECNICAS.md** - Análisis técnico
3. **PRUEBAS_MANUALES.md** - Casos de prueba
4. **RESUMEN_EJECUTIVO.md** - Resumen completo
5. **REFERENCIA_RAPIDA.md** - Este documento

---

## 🔗 RELACIONES DE DATOS

```
User (auth.User)
├─ Group (Operario, Jefe, Admin)
├─ ordenes_creadas (reverse: OrdenDeTrabajo)
├─ ordenes_asignadas (reverse: OrdenDeTrabajo)
└─ consumos_registrados (reverse: ConsumoSuministro)

OrdenDeTrabajo
├─ operario_creador → User
├─ operario_asignado → User
├─ consumos → ConsumoSuministro (reverse)
└─ estados: Pendiente → En Progreso → Cerrada

Suministro
└─ consumos → ConsumoSuministro (reverse)

ConsumoSuministro
├─ orden_de_trabajo → OrdenDeTrabajo
├─ suministro → Suministro
└─ operario_registra → User
```

---

## ⚙️ VARIABLES DE ENTORNO (si es necesario)

```bash
# .env (opcional)
DEBUG=True
SECRET_KEY=django-insecure-6c05s4$6h@9np9_u-6b(rzs7l!q&05cyi^zjswd(_vt@vat_nm
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 📞 CONTACTO PARA SOPORTE

- Ver ESPECIFICACIONES_TECNICAS.md para análisis técnico
- Ver PRUEBAS_MANUALES.md para casos de prueba
- Ver README.md para troubleshooting

---

**Última actualización:** 13 de Noviembre de 2025  
**Versión:** 1.0

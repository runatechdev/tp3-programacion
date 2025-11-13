# 🧪 GUÍA DE PRUEBAS MANUALES - MantenimientoFlow

## Checklist de Verificación del Sistema

**Proyecto:** MantenimientoFlow  
**Fecha:** 13 de Noviembre de 2025  
**Verificador:** [Tu nombre]

---

## 1. CONFIGURACIÓN INICIAL

- [ ] **1.1** Proyecto descargado y en carpeta correcta
- [ ] **1.2** Entorno virtual creado y activado
- [ ] **1.3** Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] **1.4** Migraciones aplicadas (`python manage.py migrate`)
- [ ] **1.5** Datos de prueba creados (`python manage.py crear_datos_prueba`)
- [ ] **1.6** Servidor de desarrollo ejecutándose (`python manage.py runserver`)

---

## 2. PRUEBAS DE AUTENTICACIÓN

### 2.1 Login - Usuario Válido ✅
**Pasos:**
1. Acceder a http://127.0.0.1:8000/login/
2. Ingresar usuario: `admin`
3. Ingresar contraseña: `admin123`
4. Click en "Iniciar Sesión"

**Resultado esperado:**
- [ ] Se redirige a lista de órdenes
- [ ] Mensaje: "¡Bienvenido admin!"
- [ ] Navbar muestra "admin" como usuario actual
- [ ] Botones según rol visible

### 2.2 Login - Usuario Inválido ❌
**Pasos:**
1. Acceder a http://127.0.0.1:8000/login/
2. Ingresar usuario: `usuario_falso`
3. Ingresar contraseña: `password123`
4. Click en "Iniciar Sesión"

**Resultado esperado:**
- [ ] No redirige (recarga el formulario)
- [ ] Mensaje de error: "Usuario o contraseña incorrectos"
- [ ] Permanece en página login

### 2.3 Logout
**Pasos:**
1. Estar logueado como cualquier usuario
2. Click en botón "Cerrar Sesión" en navbar

**Resultado esperado:**
- [ ] Sesión se cierra
- [ ] Redirige a página de login
- [ ] Mensaje: "Sesión cerrada correctamente"
- [ ] Navegar a /lista-ordenes redirige a login

### 2.4 Acceso sin autenticar
**Pasos:**
1. Abrir nueva pestaña/incógnito
2. Acceder a http://127.0.0.1:8000/

**Resultado esperado:**
- [ ] Redirige automáticamente a /login/

---

## 3. PRUEBAS DE SESIONES

### 3.1 Última orden visualizada
**Pasos (como admin):**
1. Ir a detalle de orden #1
2. Ir a detalle de orden #3
3. Volver a lista de órdenes
4. En la parte superior debe aparecer "Acceso rápido" a orden #3

**Resultado esperado:**
- [ ] Se muestra sección "Acceso rápido"
- [ ] Muestra la última orden visualizada (#3)
- [ ] Click redirige a detalle orden #3

### 3.2 Timeout de sesión (15 minutos)
**Pasos:**
1. Loguearse como operario1
2. Esperar 15 minutos SIN realizar acciones
3. Intentar hacer cualquier acción (click en botón, etc.)

**Resultado esperado:**
- [ ] Sesión se cierra automáticamente
- [ ] Redirige a login
- [ ] Mensaje: "Tu sesión ha expirado por inactividad (15 minutos)"

---

## 4. PRUEBAS DE ROLES Y PERMISOS

### 4.1 Operario - Crear Orden

**Login:** operario1 / oper123

**Pasos:**
1. Click en "Crear Nueva Orden de Trabajo"
2. Completar:
   - Título: "Motor principal defectuoso"
   - Fecha: Hoy
   - Descripción: "El motor presenta ruidos extraños y está completamente detenido. Necesita diagnóstico urgente."
   - Prioridad: Alta
3. Submit

**Resultado esperado:**
- [ ] Formulario se muestra correctamente
- [ ] Todos los campos presentes: titulo, fecha, descripcion, prioridad
- [ ] Campo fecha es tipo date input
- [ ] Orden se crea exitosamente
- [ ] Aparece mensaje: "Orden de trabajo #X creada exitosamente!"
- [ ] operario_creador se asigna automáticamente
- [ ] operario_asignado = NULL (sin asignar)
- [ ] estado = "Pendiente"

### 4.2 Operario - Validación descripción corta ❌
**Login:** operario1 / oper123

**Pasos:**
1. Crear orden con descripción: "Falla" (< 20 caracteres)
2. Submit

**Resultado esperado:**
- [ ] Error de validación
- [ ] Mensaje: "La descripción debe tener al menos 20 caracteres"

### 4.3 Operario - Validación fecha futura ❌
**Login:** operario1 / oper123

**Pasos:**
1. Crear orden con fecha: 15 días en el futuro
2. Submit

**Resultado esperado:**
- [ ] Error de validación
- [ ] Mensaje: "La fecha debe ser la actual o una fecha futura"

### 4.4 Operario - Validación prioridad Alta sin palabras clave ❌
**Login:** operario1 / oper123

**Pasos:**
1. Crear orden:
   - Descripción: "Hay un problema con la máquina número tres que no funciona correctamente"
   - Prioridad: Alta
2. Submit

**Resultado esperado:**
- [ ] Error de validación
- [ ] Mensaje: "Para prioridad ALTA, la descripción debe contener palabras clave..."
- [ ] Lista palabras válidas: detenido, bloqueado, fuego, urgente, etc.

### 4.5 Operario - Validación prioridad Alta CON palabras clave ✅
**Login:** operario1 / oper123

**Pasos:**
1. Crear orden:
   - Descripción: "El motor está completamente detenido y bloqueado. Necesita reparación urgente."
   - Prioridad: Alta
2. Submit

**Resultado esperado:**
- [ ] Orden se crea exitosamente
- [ ] No hay errores
- [ ] Mensaje de éxito

### 4.6 Operario - Ver solo sus órdenes
**Login:** operario1 / oper123

**Pasos:**
1. Ir a lista de órdenes
2. Verificar órdenes mostradas

**Resultado esperado:**
- [ ] Solo muestra órdenes donde:
  - operario_creador = operario1 O
  - operario_asignado = operario1
- [ ] NO muestra órdenes de otros operarios
- [ ] Contar: debe haber 3 órdenes (creó 1 + le asignaron 2)

### 4.7 Operario - No ve botón Eliminar
**Login:** operario1 / oper123

**Pasos:**
1. Ir a lista de órdenes
2. Buscar botón "Eliminar" en cada orden

**Resultado esperado:**
- [ ] NO aparece botón "Eliminar"
- [ ] NO tiene acceso a /orden/X/eliminar/

### 4.8 Operario - Ve botón Asignar/Editar ❌
**Login:** operario1 / oper123

**Pasos:**
1. Ir a lista de órdenes
2. Buscar botón "Asignar/Editar"

**Resultado esperado:**
- [ ] NO aparece botón "Asignar/Editar"
- [ ] Intento de acceso a /orden/X/asignar/ → Forbidden 403

---

## 5. PRUEBAS DE JEFE DE TALLER

### 5.1 Jefe - Ver todas las órdenes
**Login:** jefe1 / jefe123

**Pasos:**
1. Ir a lista de órdenes

**Resultado esperado:**
- [ ] Muestra TODAS las órdenes del sistema (6 órdenes)
- [ ] No filtradas por usuario
- [ ] Rol mostrado: "Jefe de Taller"

### 5.2 Jefe - Asignar orden
**Login:** jefe1 / jefe123

**Pasos:**
1. Click en "Asignar/Editar" en orden #1
2. Cambiar operario_asignado a "operario2"
3. Cambiar estado a "En Progreso"
4. Submit

**Resultado esperado:**
- [ ] Formulario muestra:
  - operario_asignado: dropdown con solo operarios
  - estado: dropdown con [Pendiente, En Progreso, Cerrada]
  - fecha_cierre_real: campo vacio (no obligatorio)
- [ ] Cambios se guardan
- [ ] Mensaje: "Orden #1 actualizada exitosamente!"
- [ ] orden.operario_asignado = operario2
- [ ] orden.estado = "En Progreso"

### 5.3 Jefe - Cerrar orden sin fecha ❌
**Login:** jefe1 / jefe123

**Pasos:**
1. Click en "Asignar/Editar" en orden #2
2. Cambiar estado a "Cerrada"
3. NO completar fecha_cierre_real
4. Submit

**Resultado esperado:**
- [ ] Error de validación
- [ ] Mensaje: "La fecha de cierre real es obligatoria cuando el estado es 'Cerrada'"
- [ ] Orden no se guarda

### 5.4 Jefe - Cerrar orden con fecha ✅
**Login:** jefe1 / jefe123

**Pasos:**
1. Click en "Asignar/Editar" en orden #2
2. Cambiar estado a "Cerrada"
3. Llenar fecha_cierre_real: hoy a las 14:30
4. Submit

**Resultado esperado:**
- [ ] Orden se guarda
- [ ] estado = "Cerrada"
- [ ] fecha_cierre_real se registra
- [ ] Mensaje de éxito

### 5.5 Jefe - Fecha cierre no puede ser futura ❌
**Login:** jefe1 / jefe123

**Pasos:**
1. Click en "Asignar/Editar"
2. Cambiar estado a "Cerrada"
3. Ingresar fecha_cierre_real = Mañana a las 10:00
4. Submit

**Resultado esperado:**
- [ ] Error de validación
- [ ] Mensaje: "La fecha de cierre no puede ser futura"

### 5.6 Jefe - Acceso a panel admin
**Login:** jefe1 / jefe123

**Pasos:**
1. Navegar a http://127.0.0.1:8000/admin/

**Resultado esperado:**
- [ ] Acceso permitido (is_staff = True)
- [ ] Ve panel de admin completo
- [ ] Puede editar órdenes, suministros, usuarios

### 5.7 Jefe - NO ve botón Eliminar
**Login:** jefe1 / jefe123

**Pasos:**
1. Ir a lista de órdenes
2. Buscar botón "Eliminar"

**Resultado esperado:**
- [ ] NO aparece botón "Eliminar"

---

## 6. PRUEBAS DE ADMINISTRADOR

### 6.1 Admin - Ve botón Eliminar
**Login:** admin / admin123

**Pasos:**
1. Ir a lista de órdenes
2. Buscar botón "Eliminar"

**Resultado esperado:**
- [ ] Aparece botón "🗑️ Eliminar" en todas las órdenes

### 6.2 Admin - Eliminar orden
**Login:** admin / admin123

**Pasos:**
1. Click en "Eliminar" de orden #1
2. Se muestra página de confirmación
3. Click en "Confirmar Eliminación"

**Resultado esperado:**
- [ ] Orden se elimina
- [ ] Redirige a lista de órdenes
- [ ] Mensaje: "Orden #1 'Título' eliminada exitosamente"
- [ ] La orden desaparece de la lista

### 6.3 Admin - Acceso a panel admin
**Login:** admin / admin123

**Pasos:**
1. Navegar a http://127.0.0.1:8000/admin/

**Resultado esperado:**
- [ ] Acceso completo
- [ ] Ver todas las secciones:
  - Usuarios
  - Grupos
  - Órdenes de Trabajo
  - Suministros
  - Consumos de Suministros

### 6.4 Admin - Permisos completos
**Login:** admin / admin123

**Pasos:**
1. Verificar que puede realizar TODAS las acciones:
   - Crear orden
   - Asignar orden
   - Registrar consumo
   - Eliminar orden
   - Acceder a admin

**Resultado esperado:**
- [ ] Todos los permisos funcionales

---

## 7. PRUEBAS DE CONSUMO DE SUMINISTROS

### 7.1 Operario - Registrar consumo
**Login:** operario2 / oper123

**Pasos:**
1. Ir a "Registrar Consumo de Suministro"
2. Seleccionar:
   - Orden de trabajo: Una de sus órdenes (estado Pendiente/En Progreso)
   - Suministro: "Tornillos M8 x 20mm"
   - Cantidad: 10
3. Submit

**Resultado esperado:**
- [ ] Formulario muestra solo órdenes abiertas del usuario
- [ ] Suministros filtrados: solo los con stock > 0
- [ ] Consumo se registra
- [ ] Mensaje: "✅ Consumo registrado exitosamente! 10 x Tornillos M8 x 20mm..."
- [ ] Stock se reduce automáticamente: 500 - 10 = 490

### 7.2 Validación stock insuficiente ❌
**Login:** operario1 / oper123

**Pasos:**
1. Ir a "Registrar Consumo"
2. Seleccionar:
   - Suministro: "Correa Transmisión A-42" (stock actual: 13)
   - Cantidad: 20 (mayor que stock)
3. Submit

**Resultado esperado:**
- [ ] Error de validación
- [ ] Mensaje: "Stock insuficiente. Disponible: 13, Solicitado: 20"
- [ ] Consumo NO se registra

### 7.3 Stock se actualiza automáticamente
**Login:** admin / admin123

**Pasos:**
1. Ir a admin: http://127.0.0.1:8000/admin/gestion_mantenimiento/suministro/
2. Ver stock de "Tornillos M8 x 20mm"
3. Nota el valor (ej: 470)
4. Ir a /consumo-suministro/ como operario
5. Registrar consumo: 30 Tornillos
6. Volver a admin

**Resultado esperado:**
- [ ] Stock se actualiza automáticamente
- [ ] Nuevo valor: 470 - 30 = 440
- [ ] Sin necesidad de guardar manualmente en vista

### 7.4 No puede registrar cantidad 0 o negativa ❌
**Login:** operario1 / oper123

**Pasos:**
1. Ir a "Registrar Consumo"
2. Ingresa cantidad: 0 o -5
3. Submit

**Resultado esperado:**
- [ ] Error de validación
- [ ] Mensaje: "La cantidad debe ser mayor a 0"

---

## 8. PRUEBAS DE FILTROS

### 8.1 Filtrar por estado
**Login:** admin / admin123

**Pasos:**
1. Ir a lista de órdenes
2. Click en botón "Pendientes"

**Resultado esperado:**
- [ ] Muestra solo órdenes con estado="Pendiente"
- [ ] Cambiar a "En Progreso" → muestra solo esas
- [ ] Cambiar a "Cerradas" → muestra solo esas
- [ ] Click en "Todos" → muestra todas

### 8.2 Filtro persiste en URL
**Pasos:**
1. Aplicar filtro estado="Pendiente"
2. URL cambia a: `/?estado=Pendiente`
3. Refrescar página F5

**Resultado esperado:**
- [ ] Filtro se mantiene aplicado
- [ ] Sigue mostrando solo Pendientes

---

## 9. PRUEBAS DE DETALLE ORDEN

### 9.1 Ver detalle orden
**Login:** operario1 / oper123

**Pasos:**
1. En lista de órdenes, click en "Ver Detalle"

**Resultado esperado:**
- [ ] Se muestra página con:
  - Información general (titulo, fecha, prioridad, estado)
  - Información de asignación (creada por, asignada a)
  - Descripción de la falla
  - Tabla de suministros consumidos
  - Botones de acción

### 9.2 Operario ve solo sus órdenes
**Login:** operario1 / oper123

**Pasos:**
1. Obtener ID de una orden de otro operario
2. Navegar a /orden/[id]/

**Resultado esperado:**
- [ ] Acceso denegado (Forbidden 403)
- [ ] Mensaje: "No tienes permisos para ver esta orden"

### 9.3 Jefe ve todas
**Login:** jefe1 / jefe123

**Pasos:**
1. Acceder a detalle de cualquier orden

**Resultado esperado:**
- [ ] Acceso permitido
- [ ] Ve toda la información

---

## 10. PRUEBAS DE INTERFAZ

### 10.1 Navbar visible
**En cualquier página logueado:**

**Verifica:**
- [ ] Logo "MantenimientoFlow"
- [ ] Links: Home, Crear Orden (si Operario), Registrar Consumo (si Operario)
- [ ] Información usuario actual
- [ ] Botón "Cerrar Sesión"
- [ ] Estilos responsive

### 10.2 Mensajes visibles
**Después de cada acción:**

**Verifica:**
- [ ] Mensajes success (color verde)
- [ ] Mensajes error (color rojo)
- [ ] Mensajes info (color azul)
- [ ] Desaparecen después de X segundos o click

### 10.3 Botones deshabilitados correctamente
**Para cada rol:**

**Verifica:**
- [ ] Operario: Sin Asignar/Editar, Sin Eliminar
- [ ] Jefe: Con Asignar/Editar, Sin Eliminar
- [ ] Admin: Con Asignar/Editar, Con Eliminar

---

## 11. PRUEBAS DE DATOS DE PRUEBA

### 11.1 Comando crear_datos_prueba
**Pasos:**
```bash
python manage.py crear_datos_prueba
```

**Resultado esperado:**
- [ ] Se muestra tabla con credenciales
- [ ] 6 órdenes creadas
- [ ] 10+ suministros creados
- [ ] 3 consumos registrados

### 11.2 Órdenes incluyen contexto
**Login:** admin / admin123

**Pasos:**
1. Ir a lista de órdenes
2. Verificar órdenes de ejemplo

**Resultado esperado:**
- [ ] Orden 1: "Motor principal detenido - URGENTE" (Alta)
- [ ] Orden 2: "Fuga de aceite en compresor" (Media)
- [ ] Orden 3: "Ruido anormal en caja reductora" (Media)
- [ ] Orden 4: "Sistema eléctrico en cortocircuito" (Alta)
- [ ] Orden 5: "Cambio de filtros" (Baja)
- [ ] Orden 6: "Reparación de correa" (Alta, Cerrada)

---

## 12. CASOS EDGE / NEGATIVOS

### 12.1 Usuario sin grupo
**Pasos:**
1. En admin, crear usuario sin grupo
2. Intentar loguearse

**Resultado esperado:**
- [ ] Acceso permitido a login
- [ ] Ve lista vacía o lista completa (según código)
- [ ] No puede crear orden (sin Operario)
- [ ] No puede asignar (sin Jefe)

### 12.2 Orden con múltiples consumos
**Login:** admin / admin123

**Pasos:**
1. Registrar 3 consumos diferentes para misma orden
2. Ir a detalle

**Resultado esperado:**
- [ ] Tabla muestra los 3 consumos
- [ ] Cada uno con fecha, cantidad, registrado por

### 12.3 Suministro con stock 0
**Pasos:**
1. En admin, poner stock de un suministro a 0
2. Como Operario, intentar registrar consumo

**Resultado esperado:**
- [ ] Suministro NO aparece en dropdown
- [ ] (filtrado por stock > 0)

---

## 13. CHECKLIST FINAL

### Requisitos del TP cumplidos:

- [ ] ✅ Modelos: OrdenDeTrabajo, Suministro, ConsumoSuministro
- [ ] ✅ Campo `fecha` en OrdenDeTrabajo
- [ ] ✅ Tres roles: Operario, Jefe, Admin
- [ ] ✅ Permisos asignados correctamente
- [ ] ✅ Autenticación: Login/Logout
- [ ] ✅ Sesiones: Guardar última orden
- [ ] ✅ Timeout: 15 minutos inactividad
- [ ] ✅ Formulario 1: OrdenDeTrabajoForm con validaciones
- [ ] ✅ Formulario 2: ConsumoSuministroForm con validaciones
- [ ] ✅ Formulario 3: AsignacionYEstadoForm con validaciones
- [ ] ✅ Vista lista: Filtrar por rol
- [ ] ✅ Vista crear: Solo Operarios
- [ ] ✅ Vista consumo: Solo Operarios
- [ ] ✅ Vista asignar: Solo Jefes/Admins
- [ ] ✅ Vista eliminar: Solo Admins con permiso
- [ ] ✅ Botón Eliminar: Solo si tiene permiso
- [ ] ✅ Stock se actualiza automáticamente
- [ ] ✅ Validaciones a nivel campo y formulario
- [ ] ✅ Comando crear_datos_prueba

### Calidad del código:

- [ ] ✅ Código limpio y comentado
- [ ] ✅ Nombres descriptivos
- [ ] ✅ Seguir convenciones Django
- [ ] ✅ Seguridad: CSRF, SQL injection, XSS
- [ ] ✅ ORM optimizado (select_related, filter)
- [ ] ✅ Documentación en README

---

## RESULTADO FINAL

**Fecha de prueba:** _____________  
**Probador:** _____________  
**Resultado:**

- [ ] ✅ TODOS LOS TESTS PASARON
- [ ] ⚠️ ALGUNOS TESTS FALLARON (especificar)
- [ ] ❌ LA MAYORÍA DE TESTS FALLARON

**Observaciones:**
```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

**Firma:** _________________________

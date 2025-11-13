from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from gestion_mantenimiento.models import OrdenDeTrabajo, Suministro, ConsumoSuministro
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Crea datos de prueba completos para el sistema MantenimientoFlow'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=== Creando datos de prueba ===\n'))
        
        # 1. Crear Grupos
        self.stdout.write('1. Creando grupos...')
        grupo_operario, _ = Group.objects.get_or_create(name='Operario')
        grupo_jefe, _ = Group.objects.get_or_create(name='Jefe de Taller')
        grupo_admin, _ = Group.objects.get_or_create(name='Administrador')
        
        # 2. Asignar permisos a los grupos
        self.stdout.write('2. Asignando permisos...')
        
        # Permisos para Operario
        content_type_orden = ContentType.objects.get_for_model(OrdenDeTrabajo)
        content_type_consumo = ContentType.objects.get_for_model(ConsumoSuministro)
        
        perm_add_orden = Permission.objects.get(codename='add_ordendetrabajo', content_type=content_type_orden)
        perm_add_consumo = Permission.objects.get(codename='add_consumosuministro', content_type=content_type_consumo)
        grupo_operario.permissions.add(perm_add_orden, perm_add_consumo)
        
        # Permisos para Jefe de Taller
        perm_change_orden = Permission.objects.get(codename='change_ordendetrabajo', content_type=content_type_orden)
        perm_view_orden = Permission.objects.get(codename='view_ordendetrabajo', content_type=content_type_orden)
        
        content_type_suministro = ContentType.objects.get_for_model(Suministro)
        perm_change_suministro = Permission.objects.get(codename='change_suministro', content_type=content_type_suministro)
        perm_delete_suministro = Permission.objects.get(codename='delete_suministro', content_type=content_type_suministro)
        perm_add_suministro = Permission.objects.get(codename='add_suministro', content_type=content_type_suministro)
        
        grupo_jefe.permissions.add(
            perm_add_orden, perm_change_orden, perm_view_orden,
            perm_add_suministro, perm_change_suministro, perm_delete_suministro,
            perm_add_consumo
        )
        
        # Permisos para Administrador (todos)
        perm_delete_orden = Permission.objects.get(codename='delete_ordendetrabajo', content_type=content_type_orden)
        all_permissions = Permission.objects.all()
        grupo_admin.permissions.set(all_permissions)
        
        # 3. Crear Usuarios
        self.stdout.write('3. Creando usuarios...')
        
        # Crear Administrador (superuser)
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@mantenimiento.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            admin.groups.add(grupo_admin)
            self.stdout.write(self.style.SUCCESS('  ✓ Admin creado: admin / admin123'))
        
        # Crear Jefes de Taller
        jefes_data = [
            {'username': 'jefe1', 'password': 'jefe123', 'first_name': 'Carlos', 'last_name': 'Rodríguez'},
            {'username': 'jefe2', 'password': 'jefe123', 'first_name': 'María', 'last_name': 'González'},
        ]
        
        jefes = []
        for data in jefes_data:
            if not User.objects.filter(username=data['username']).exists():
                jefe = User.objects.create_user(
                    username=data['username'],
                    email=f"{data['username']}@mantenimiento.com",
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    is_staff=True
                )
                jefe.groups.add(grupo_jefe)
                jefes.append(jefe)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Jefe creado: {data['username']} / {data['password']}"))
        
        # Crear Operarios
        operarios_data = [
            {'username': 'operario1', 'password': 'oper123', 'first_name': 'Juan', 'last_name': 'Pérez'},
            {'username': 'operario2', 'password': 'oper123', 'first_name': 'Ana', 'last_name': 'Martínez'},
            {'username': 'operario3', 'password': 'oper123', 'first_name': 'Luis', 'last_name': 'García'},
            {'username': 'operario4', 'password': 'oper123', 'first_name': 'Pedro', 'last_name': 'López'},
        ]
        
        operarios = []
        for data in operarios_data:
            if not User.objects.filter(username=data['username']).exists():
                operario = User.objects.create_user(
                    username=data['username'],
                    email=f"{data['username']}@mantenimiento.com",
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name']
                )
                operario.groups.add(grupo_operario)
                operarios.append(operario)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Operario creado: {data['username']} / {data['password']}"))
        
        # 4. Crear Suministros
        self.stdout.write('4. Creando suministros...')
        
        suministros_data = [
            {'nombre': 'Tornillos M8 x 20mm', 'descripcion': 'Tornillos métricos para uso general', 'stock': 500, 'precio': 0.50},
            {'nombre': 'Tuercas M8', 'descripcion': 'Tuercas métricas para tornillos M8', 'stock': 450, 'precio': 0.30},
            {'nombre': 'Aceite Motor 10W40', 'descripcion': 'Aceite sintético para motores', 'stock': 50, 'precio': 25.00},
            {'nombre': 'Filtro de Aceite', 'descripcion': 'Filtro de aceite universal', 'stock': 30, 'precio': 15.00},
            {'nombre': 'Grasa Industrial', 'descripcion': 'Grasa multiusos para rodamientos', 'stock': 20, 'precio': 12.00},
            {'nombre': 'Cable Eléctrico 2.5mm', 'descripcion': 'Cable eléctrico por metro', 'stock': 200, 'precio': 2.50},
            {'nombre': 'Fusibles 10A', 'descripcion': 'Fusibles de protección 10 amperios', 'stock': 100, 'precio': 1.00},
            {'nombre': 'Correa Transmisión A-42', 'descripcion': 'Correa en V para maquinaria', 'stock': 15, 'precio': 45.00},
            {'nombre': 'Rodamiento 6205', 'descripcion': 'Rodamiento rígido de bolas', 'stock': 25, 'precio': 18.00},
            {'nombre': 'Soldadura Electrodo E6013', 'descripcion': 'Electrodos para soldadura por kilo', 'stock': 80, 'precio': 8.00},
        ]
        
        suministros = []
        for data in suministros_data:
            suministro, created = Suministro.objects.get_or_create(
                nombre=data['nombre'],
                defaults={
                    'descripcion': data['descripcion'],
                    'stock': data['stock'],
                    'precio_unitario': data['precio']
                }
            )
            suministros.append(suministro)
            if created:
                self.stdout.write(f"  ✓ Suministro creado: {data['nombre']}")
        
        # 5. Crear Órdenes de Trabajo
        self.stdout.write('5. Creando órdenes de trabajo...')
        
        # Obtener operarios y jefes creados (si no existen, usar los que ya están)
        operarios = list(User.objects.filter(groups__name='Operario'))
        
        if not operarios:
            self.stdout.write(self.style.WARNING('  ⚠ No hay operarios creados'))
            return
        
        ordenes_data = [
            {
                'titulo': 'Motor principal detenido - URGENTE',
                'fecha': timezone.now().date(),
                'descripcion': 'El motor principal está completamente detenido y bloqueado, impidiendo la producción. Necesita revisión urgente de sistema eléctrico y mecánico.',
                'prioridad': 'Alta',
                'estado': 'Pendiente',
                'operario_idx': 0
            },
            {
                'titulo': 'Fuga de aceite en compresor',
                'fecha': timezone.now().date() - timedelta(days=1),
                'descripcion': 'Se detectó una fuga considerable de aceite en el compresor de aire. Requiere cambio de sellos y verificación de niveles.',
                'prioridad': 'Media',
                'estado': 'En Progreso',
                'operario_idx': 1,
                'asignado_idx': 1
            },
            {
                'titulo': 'Ruido anormal en caja reductora',
                'fecha': timezone.now().date() - timedelta(days=2),
                'descripcion': 'La caja reductora de la línea 3 presenta ruidos anormales durante el funcionamiento. Posible desgaste de rodamientos o engranajes.',
                'prioridad': 'Media',
                'estado': 'Pendiente',
                'operario_idx': 2
            },
            {
                'titulo': 'Sistema eléctrico en cortocircuito',
                'fecha': timezone.now().date(),
                'descripcion': 'Panel eléctrico principal presenta falla crítica con cortocircuito constante. Equipo completamente inoperativo y bloqueado por seguridad.',
                'prioridad': 'Alta',
                'estado': 'En Progreso',
                'operario_idx': 0,
                'asignado_idx': 2
            },
            {
                'titulo': 'Cambio de filtros mantenimiento preventivo',
                'fecha': timezone.now().date() + timedelta(days=1),
                'descripcion': 'Mantenimiento preventivo programado para cambio de filtros de aceite y aire en todas las unidades. Tarea rutinaria de mantenimiento.',
                'prioridad': 'Baja',
                'estado': 'Pendiente',
                'operario_idx': 3
            },
            {
                'titulo': 'Reparación de correa transmisión',
                'fecha': timezone.now().date() - timedelta(days=3),
                'descripcion': 'La correa de transmisión del motor auxiliar está desgastada y requiere reemplazo inmediato para evitar paradas. Vibración excesiva detectada.',
                'prioridad': 'Alta',
                'estado': 'Cerrada',
                'operario_idx': 1,
                'asignado_idx': 1,
                'cerrada': True
            },
        ]
        
        ordenes = []
        for data in ordenes_data:
            orden, created = OrdenDeTrabajo.objects.get_or_create(
                titulo=data['titulo'],
                defaults={
                    'fecha': data['fecha'],
                    'descripcion_falla': data['descripcion'],
                    'prioridad': data['prioridad'],
                    'estado': data['estado'],
                    'operario_creador': operarios[data['operario_idx']],
                    'operario_asignado': operarios[data.get('asignado_idx', data['operario_idx'])] if 'asignado_idx' in data or True else None,
                }
            )
            
            if created:
                if data.get('cerrada'):
                    orden.fecha_cierre_real = timezone.now() - timedelta(hours=2)
                    orden.save()
                
                ordenes.append(orden)
                self.stdout.write(f"  ✓ Orden creada: {data['titulo'][:50]}...")
        
        # 6. Crear algunos consumos de prueba
        self.stdout.write('6. Creando consumos de suministros...')
        
        if ordenes and suministros:
            # Consumos para la orden cerrada
            orden_cerrada = OrdenDeTrabajo.objects.filter(estado='Cerrada').first()
            if orden_cerrada:
                consumos_data = [
                    {'suministro_idx': 7, 'cantidad': 2},  # Correas
                    {'suministro_idx': 8, 'cantidad': 4},  # Rodamientos
                    {'suministro_idx': 0, 'cantidad': 20},  # Tornillos
                ]
                
                for data in consumos_data:
                    try:
                        consumo, created = ConsumoSuministro.objects.get_or_create(
                            orden_de_trabajo=orden_cerrada,
                            suministro=suministros[data['suministro_idx']],
                            defaults={
                                'cantidad_usada': data['cantidad'],
                                'operario_registra': orden_cerrada.operario_asignado
                            }
                        )
                        if created:
                            self.stdout.write(f"  ✓ Consumo registrado: {data['cantidad']} x {suministros[data['suministro_idx']].nombre}")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"  ⚠ Error creando consumo: {e}"))
        
        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE\n'))
        self.stdout.write(self.style.SUCCESS('CREDENCIALES DE ACCESO:'))
        self.stdout.write(self.style.SUCCESS('─'*50))
        self.stdout.write(self.style.SUCCESS('👑 Administrador:'))
        self.stdout.write('   Usuario: admin | Password: admin123')
        self.stdout.write(self.style.SUCCESS('\n👔 Jefes de Taller:'))
        self.stdout.write('   Usuario: jefe1 | Password: jefe123')
        self.stdout.write('   Usuario: jefe2 | Password: jefe123')
        self.stdout.write(self.style.SUCCESS('\n🔧 Operarios:'))
        self.stdout.write('   Usuario: operario1 | Password: oper123')
        self.stdout.write('   Usuario: operario2 | Password: oper123')
        self.stdout.write('   Usuario: operario3 | Password: oper123')
        self.stdout.write('   Usuario: operario4 | Password: oper123')
        self.stdout.write(self.style.SUCCESS('─'*50))
        self.stdout.write(f'📋 Órdenes creadas: {OrdenDeTrabajo.objects.count()}')
        self.stdout.write(f'📦 Suministros creados: {Suministro.objects.count()}')
        self.stdout.write(f'🔄 Consumos registrados: {ConsumoSuministro.objects.count()}')
        self.stdout.write('='*50 + '\n')

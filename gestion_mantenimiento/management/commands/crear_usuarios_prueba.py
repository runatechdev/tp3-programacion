from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Crea usuarios y grupos de prueba para MantenimientoFlow'

    def handle(self, *args, **options):
        # Crear grupos
        operario_group, created = Group.objects.get_or_create(name='Operario')
        jefe_group, created = Group.objects.get_or_create(name='Jefe de Taller')
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Grupos creados exitosamente'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Los grupos ya existían'))

        # Usuarios de prueba
        usuarios_data = [
            # Operarios
            {'username': 'operario1', 'group': operario_group, 'email': 'operario1@empresa.com', 'first_name': 'Juan', 'last_name': 'Pérez'},
            {'username': 'operario2', 'group': operario_group, 'email': 'operario2@empresa.com', 'first_name': 'María', 'last_name': 'López'},
            {'username': 'operario3', 'group': operario_group, 'email': 'operario3@empresa.com', 'first_name': 'Pedro', 'last_name': 'García'},
            
            # Jefes de Taller
            {'username': 'jefe1', 'group': jefe_group, 'email': 'jefe1@empresa.com', 'first_name': 'Carlos', 'last_name': 'Gómez'},
            {'username': 'jefe2', 'group': jefe_group, 'email': 'jefe2@empresa.com', 'first_name': 'Ana', 'last_name': 'Rodríguez'},
            
            # Administradores
            {'username': 'admin', 'group': admin_group, 'email': 'admin@mantenimientoflow.com', 'first_name': 'Super', 'last_name': 'Administrador', 'is_superuser': True, 'is_staff': True},
            {'username': 'gerente', 'group': admin_group, 'email': 'gerente@empresa.com', 'first_name': 'Laura', 'last_name': 'Martínez'},
        ]

        for user_data in usuarios_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_superuser': user_data.get('is_superuser', False),
                    'is_staff': user_data.get('is_staff', False),
                }
            )
            user.set_password('1234')
            user.groups.add(user_data['group'])
            user.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Usuario {user_data["username"]} creado'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Usuario {user_data["username"]} ya existía - Actualizado'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Usuarios de prueba creados exitosamente!'))
        self.stdout.write('📋 Credenciales de acceso (todos usan contraseña: 1234):')
        self.stdout.write('')
        self.stdout.write('👷 OPERARIOS:')
        self.stdout.write('   operario1 / 1234 - Juan Pérez')
        self.stdout.write('   operario2 / 1234 - María López') 
        self.stdout.write('   operario3 / 1234 - Pedro García')
        self.stdout.write('')
        self.stdout.write('👨‍💼 JEFES DE TALLER:')
        self.stdout.write('   jefe1 / 1234 - Carlos Gómez')
        self.stdout.write('   jefe2 / 1234 - Ana Rodríguez')
        self.stdout.write('')
        self.stdout.write('👑 ADMINISTRADORES:')
        self.stdout.write('   admin / 1234 - Super Administrador (Superuser)')
        self.stdout.write('   gerente / 1234 - Laura Martínez')
        self.stdout.write('')
        self.stdout.write('💡 Nota: El usuario "admin" tiene acceso completo al sistema y al panel de administración Django.')
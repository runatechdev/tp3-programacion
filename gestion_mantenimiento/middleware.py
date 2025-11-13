from django.contrib.auth import logout
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages


class SessionTimeoutMiddleware:
    """
    Middleware para cerrar la sesión automáticamente después de 15 minutos de inactividad
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Obtener el último acceso de la sesión
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                # Convertir a timestamp
                last_activity_time = timezone.datetime.fromtimestamp(last_activity, tz=timezone.get_current_timezone())
                
                # Calcular tiempo transcurrido
                time_elapsed = timezone.now() - last_activity_time
                
                # Si han pasado más de 15 minutos (900 segundos)
                if time_elapsed.total_seconds() > 900:
                    logout(request)
                    messages.warning(request, '⚠️ Tu sesión ha expirado por inactividad (15 minutos).')
                    return redirect('gestion_mantenimiento:login')
            
            # Actualizar el último acceso
            request.session['last_activity'] = timezone.now().timestamp()
        
        response = self.get_response(request)
        return response

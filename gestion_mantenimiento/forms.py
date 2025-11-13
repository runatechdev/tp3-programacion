from django import forms
from .models import OrdenDeTrabajo, ConsumoSuministro, Suministro
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

class OrdenDeTrabajoForm(forms.ModelForm):
    """
    Formulario 1: Para que los Operarios reporten fallas
    Cumple con las validaciones requeridas:
    - descripcion_falla min_length=20
    - fecha debe ser actual o futura
    - Validación de palabras clave para prioridad Alta
    """
    
    class Meta:
        model = OrdenDeTrabajo
        fields = ['titulo', 'fecha', 'descripcion_falla', 'prioridad']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Falla en motor principal'
            }),
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'descripcion_falla': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Describa la falla en detalle (mínimo 20 caracteres)...'
            }),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'fecha': 'Fecha de Reporte',
            'descripcion_falla': 'Descripción Detallada de la Falla',
        }
        help_texts = {
            'descripcion_falla': 'Mínimo 20 caracteres. Para prioridad ALTA, incluya palabras como "detenido", "bloqueado", etc.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el campo prioridad como requerido
        self.fields['prioridad'].required = True
    
    def clean_descripcion_falla(self):
        """Validación a nivel de campo: mínimo 20 caracteres"""
        descripcion = self.cleaned_data.get('descripcion_falla', '').strip()
        if len(descripcion) < 20:
            raise ValidationError(
                "La descripción debe tener al menos 20 caracteres. "
                f"Actualmente tiene {len(descripcion)} caracteres."
            )
        return descripcion
    
    def clean_fecha(self):
        """Validación a nivel de campo: fecha debe ser actual o futura"""
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < timezone.now().date():
            raise ValidationError(
                "La fecha debe ser la actual o una fecha futura. "
                f"Fecha ingresada: {fecha}"
            )
        return fecha
    
    def clean(self):
        """
        Validación a nivel de formulario: 
        Para prioridad Alta, verificar palabras clave de urgencia
        """
        cleaned_data = super().clean()
        prioridad = cleaned_data.get('prioridad')
        descripcion = cleaned_data.get('descripcion_falla', '').lower()
        
        # Lista de palabras clave de urgencia
        palabras_urgencia = [
            'detenido', 'bloqueado', 'fuego', 'urgente', 'crítico', 
            'emergencia', 'parado', 'inoperativo', 'falla total'
        ]
        
        if prioridad == 'Alta':
            if not any(palabra in descripcion for palabra in palabras_urgencia):
                raise ValidationError({
                    'descripcion_falla': ValidationError(
                        "Para prioridad ALTA, la descripción debe contener palabras clave de urgencia como: "
                        "'detenido', 'bloqueado', 'fuego', 'urgente', 'crítico', 'emergencia'."
                    )
                })
        
        return cleaned_data


class ConsumoSuministroForm(forms.ModelForm):
    """
    Formulario 2: Para que los Operarios registren consumo de suministros
    Validaciones:
    - Verificar stock disponible
    - Fecha posterior a creación de orden
    """
    
    class Meta:
        model = ConsumoSuministro
        fields = ['orden_de_trabajo', 'suministro', 'cantidad_usada']
        widgets = {
            'orden_de_trabajo': forms.Select(attrs={'class': 'form-control'}),
            'suministro': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_usada': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Cantidad utilizada'
            }),
        }
        labels = {
            'cantidad_usada': 'Cantidad Utilizada',
        }
    
    def __init__(self, user, *args, **kwargs):
        """
        Filtra las órdenes y suministros disponibles para el usuario
        """
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Filtrar órdenes: solo las abiertas asignadas al usuario
        self.fields['orden_de_trabajo'].queryset = OrdenDeTrabajo.objects.filter(
            estado__in=['Pendiente', 'En Progreso'],
            operario_asignado=user
        ).order_by('-fecha_creacion')
        
        # Filtrar suministros: solo los que tienen stock disponible
        self.fields['suministro'].queryset = Suministro.objects.filter(
            stock__gt=0
        ).order_by('nombre')
        
        # Personalizar etiquetas
        self.fields['orden_de_trabajo'].label = "Orden de Trabajo (Abiertas)"
        self.fields['suministro'].label = "Suministro (Con stock disponible)"
        
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
    
    def clean_cantidad_usada(self):
        """Validación: cantidad mayor a 0"""
        cantidad = self.cleaned_data.get('cantidad_usada')
        if cantidad and cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad
    
    def clean(self):
        """
        Validaciones a nivel de formulario:
        - Verificar stock suficiente
        - Verificar fecha de consumo posterior a creación de orden
        """
        cleaned_data = super().clean()
        suministro = cleaned_data.get('suministro')
        cantidad_usada = cleaned_data.get('cantidad_usada')
        orden_de_trabajo = cleaned_data.get('orden_de_trabajo')
        
        # Validación CRÍTICA: Verificar stock disponible
        if suministro and cantidad_usada:
            if cantidad_usada > suministro.stock:
                raise ValidationError({
                    'cantidad_usada': ValidationError(
                        f"❌ Stock insuficiente. Disponible: {suministro.stock}, "
                        f"Solicitado: {cantidad_usada}"
                    )
                })
        
        # Validación: Fecha de consumo posterior a creación de orden
        if orden_de_trabajo and timezone.now() < orden_de_trabajo.fecha_creacion:
            raise ValidationError(
                "No se puede registrar consumo antes de la creación de la orden."
            )
        
        return cleaned_data


class AsignacionYEstadoForm(forms.ModelForm):
    """
    Formulario 3: Para Jefes de Taller asignar órdenes y cambiar estado
    Validaciones:
    - Fecha de cierre obligatoria para estado "Cerrada"
    - Fecha de cierre posterior a fecha de creación
    """
    
    class Meta:
        model = OrdenDeTrabajo
        fields = ['operario_asignado', 'estado', 'fecha_cierre_real']
        widgets = {
            'operario_asignado': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_cierre_real': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
        }
        labels = {
            'operario_asignado': 'Operario Asignado',
            'fecha_cierre_real': 'Fecha Real de Cierre',
        }
        help_texts = {
            'fecha_cierre_real': 'Obligatorio cuando el estado es "Cerrada"',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar operarios: solo usuarios del grupo Operario
        try:
            grupo_operarios = User.objects.filter(groups__name='Operario')
            self.fields['operario_asignado'].queryset = grupo_operarios
        except:
            self.fields['operario_asignado'].queryset = User.objects.none()
        
        # Hacer el campo de fecha de cierre no obligatorio inicialmente
        self.fields['fecha_cierre_real'].required = False
        
        # Agregar clases CSS
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
    
    def clean_fecha_cierre_real(self):
        """Validación: fecha de cierre no puede ser futura"""
        fecha_cierre = self.cleaned_data.get('fecha_cierre_real')
        if fecha_cierre and fecha_cierre > timezone.now():
            raise ValidationError("La fecha de cierre no puede ser futura.")
        return fecha_cierre
    
    def clean(self):
        """
        Validación a nivel de formulario:
        - Fecha de cierre obligatoria para estado "Cerrada"
        - Fecha de cierre posterior a fecha de creación
        """
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_cierre = cleaned_data.get('fecha_cierre_real')
        
        # Validación CONDICIONAL: Fecha de cierre obligatoria para estado "Cerrada"
        if estado == 'Cerrada' and not fecha_cierre:
            raise ValidationError({
                'fecha_cierre_real': ValidationError(
                    "La fecha de cierre real es obligatoria cuando el estado es 'Cerrada'."
                )
            })
        
        # Validación: Fecha de cierre posterior a fecha de creación
        if fecha_cierre and self.instance and self.instance.fecha_creacion:
            if fecha_cierre < self.instance.fecha_creacion:
                raise ValidationError({
                    'fecha_cierre_real': ValidationError(
                        "La fecha de cierre no puede ser anterior a la fecha de creación de la orden."
                    )
                })
        
        return cleaned_data
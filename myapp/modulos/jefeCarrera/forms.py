from django import forms
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget 
from myapp.modulos.jefeCarrera.models import Evento
from django.core.exceptions import ValidationError
import datetime, random, sha



class ImageUploadForm(forms.Form):
	image = forms.ImageField()

class StringListField(forms.CharField):
    def prepare_value(self, value):
        return ', '.join(str(value))
 
class AgregarEventoCordForm(forms.ModelForm):

    TIPOS2 = (
        ('profesor', 'Profesores de la Linea'),
        ('jefe', 'Solo Jefe Carrera'),
        )
    
    class Meta:
        model = Evento
        fields = ['tipoEvento']


    # summary = forms.CharField(widget = forms.TextInput(), label="Titulo del Evento:")
    # location = forms.CharField(widget = forms.TextInput(), label="Ubicacion del Evento:")
    # descripcion = forms.CharField(widget=forms.Textarea, label= "Descripcion: ")
    #fecha = forms.DateField(label = "Seleccione Fecha:" )
    # start = forms.TimeField(widget=TimeWidget,label="Hora Inicio:",  initial=datetime.date.today)
    # end = forms.TimeField(widget=TimeWidget,label="Hora Fin:",  initial=datetime.date.today)
    tipoEvento = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=TIPOS2, label="Seleccione Tipo de Evento")

class AgregarEventoForm(forms.Form):

    TIPOS = (
        ('general', 'Tipo General'),
        ('coordinadores', 'Solo Coordinadores'),
        )

     class Meta:
        model = Evento
        fields = ['tipoEvento']


    # summary = forms.CharField(widget = forms.TextInput(), label="Titulo del Evento:")
    # location = forms.CharField(widget = forms.TextInput(), label="Ubicacion del Evento:")
    # descripcion = forms.CharField(widget=forms.Textarea, label= "Descripcion: ")
    #fecha = forms.DateField(label = "Seleccione Fecha:" )
    # start = forms.TimeField(widget=TimeWidget,label="Hora Inicio:",  initial=datetime.date.today)
    # end = forms.TimeField(widget=TimeWidget,label="Hora Fin:",  initial=datetime.date.today)
    tipoEvento = forms.ChoiceField(required=True, widget=forms.RadioSelect, choices=TIPOS, label="Seleccione Tipo de Evento")


class agregarAsignaturaForm(forms.Form):
    nombreAsignatura = forms.CharField(widget = forms.TextInput(), label= "Ingresa el Nombre de la Asignatura")
    MY_CHOICES = (
        ('2001', ' 2001'),
        ('2012', ' 2012'),
    )
    plan = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES, label="Selecciona el plan que pertenece")
   

class agregarProfesoresForm(forms.Form):
    email = forms.EmailField(label="Correo Electronico", widget=forms.TextInput())

    def clean_email(self):
        email = self.cleaned_data.get('email')
        dominio =  email.split('@')[1]
        if (dominio != 'usach.cl'):

            raise ValidationError("Debes Ingresar un email del dominio USACH.")

        return self.cleaned_data.get('email', '')

class changePasswordForm(forms.Form):
    old_password = forms.CharField(label="Password Antigua", widget=forms.PasswordInput(render_value=False))
    password = forms.CharField(label="Password Nueva", widget=forms.PasswordInput(render_value=False))

class aprobacionProgramaForm(forms.Form):

    MY_CHOICES = (
        ('Si', ' Se aprueba'),
        ('No', ' No se aprueba'),
    )
    opcion = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES)

class indicacionProgramaForm(forms.Form):

    MY_CHOICES = (
        ('Si', ' Si tiene indicaciones que corregir'),
        ('No', ' No tiene indicaciones'),
    )
    opcion = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES, label= "")

class analizarFTForm(forms.Form):

    MY_CHOICES = (
        ('Si', ' Fast Track'),
        ('No', ' No debe ir a Fast Track'),
    )
    opcion = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES, label= "")
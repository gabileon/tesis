from django import forms
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget 
from myapp.modulos.jefeCarrera.models import Evento

class ImageUploadForm(forms.Form):
	image = forms.ImageField()

class StringListField(forms.CharField):
    def prepare_value(self, value):
        return ', '.join(str(value))
 
    def to_python(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(',')]

class AgregarEventoForm(forms.ModelForm):

    TIPOS = (
        ('general', 'Tipo General'),
        ('coordinadores', 'Solo Coordinadores'),
        )
    
    class Meta:
        model = Evento
        fields = ['summary', 'location', 'descripcion', 'start', 'end']

    summary = forms.CharField(widget = forms.TextInput(), label="Titulo del Evento:")
    location = forms.CharField(widget = forms.TextInput(), label="Ubicacion del Evento:")
    descripcion = forms.CharField(widget=forms.Textarea, label= "Descripcion: ")
    start = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3), label="Fecha y hora de inicio:")
    end = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3), label="Fecha y hora de termino:")
    tipoEvento = forms.ChoiceField(widget=forms.RadioSelect, choices=TIPOS)

class agregarAsignaturaForm(forms.Form):
    nombreAsignatura = forms.CharField(widget = forms.TextInput())
    MY_CHOICES = (
        ('2001', '2001'),
        ('2012', '2012'),
    )
    plan = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES)

    

class agregarProfesoresForm(forms.Form):
    email = forms.EmailField(label="Correo Electronico", widget=forms.TextInput())

class changePasswordForm(forms.Form):
    old_password = forms.CharField(label="Password Antigua", widget=forms.PasswordInput(render_value=False))
    password = forms.CharField(label="Password Nueva", widget=forms.PasswordInput(render_value=False))
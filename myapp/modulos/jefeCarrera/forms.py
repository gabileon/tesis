from django import forms
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget 

class ImageUploadForm(forms.Form):
	image = forms.ImageField()

class StringListField(forms.CharField):
    def prepare_value(self, value):
        return ', '.join(str(value))
 
    def to_python(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(',')]

class AgregarEventoForm(forms.Form):
    summary = forms.CharField(widget = forms.TextInput(), label="Titulo del Evento:")
    location = forms.CharField(widget = forms.TextInput(), label="Ubicacion del Evento:")
    descripcion = forms.CharField(widget=forms.Textarea, label= "Descripcion: ")
    start = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3), label="Fecha y hora de inicio:")
    end = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3), label="Fecha y hora de termino:")
	# attendees =  ListaField()

class agregarAsignaturaForm(forms.Form):
    nombreAsignatura = forms.CharField(widget = forms.TextInput())
    MY_CHOICES = (
        ('2001', '2001'),
        ('2012', '2012'),
    )
    plan = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES)

    
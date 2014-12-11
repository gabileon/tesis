
from django import forms
from myapp.modulos.formulacion.models import Asignatura
from django.contrib.auth.models import Group





class crearProgramaForm(forms.Form):

	SEMESTRES = (('I','I'), ('II', 'II'))
	ANOS = (('2014','2014'), ('2015', '2015'))

	# asignaturas = [(c.id, c.nombreAsig) for c in Asignatura.objects.all()]
	# asignatura = forms.ChoiceField(required=True, label='Asignatura', choices=asignaturas)
	asignatura = forms.CharField(widget=forms.TextInput())
	semestre = forms.ChoiceField(choices=SEMESTRES)
	ano = forms.ChoiceField(choices=ANOS)

	def clean(self):
		return self.cleaned_data

class estadoForm(forms.Form):
    MY_CHOICES = (
        ('opt0', 'Finalizado'),
        ('opt1', 'Modificando'),
    )
    estado = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES)

class UploadFileForm(forms.Form):
	ESTADOS = (
		('General', (u"General")),
	 	('Definicion Datos Asignatura', (u"Definicion Datos Asignatura")),
	 	('Definiciones Generales', (u"Definiciones Generales")),
	 	('Definicion de Constribucion al Perfil de Egreso', (u"Definicion de Constribucion al Perfil de Egreso ")),
	 	('Definicion Resultados de Aprendizaje', (u"Definicion Resultados de Aprendizaje")),
	 	('Estrategias de Ensenanza y de Aprendizaje', (u"Estrategias de Ensenanza y de Aprendizaje")),
	 	('Definicion de Clase a Clase', (u"Definicion de Clase a Clase")),
	 	('Analisis de evaluaciones asociadas', (u"Analisis de evaluaciones asociadas")),
	 	('Verificacion Coherencia y Completitud', (u"Verificacion Coherencia y Completitud")),
	 	('Definicion de Aspectos Administrativos', (u"Definicion de Aspectos Administrativos")),
	 	('Definicion de Recursos de Aprendizaje', (u"Definicion de Recursos de Aprendizaje")),
	 	)
	title = forms.CharField(max_length=50, label="Titulo del Recurso")
	recurso = forms.FileField(label="Seleccione el archivo")
	descripcion = forms.CharField(widget=forms.Textarea, label="Descripcion del Recurso")
	estado = forms.ChoiceField(choices=ESTADOS, label= "Seleccione el estado")
	
class LineasForm(forms.Form):
	nombreLinea  = forms.CharField(widget=forms.TextInput(),label="Nombre de Linea de Asignatura")

class analizarForm(forms.Form):
	decision = forms.CheckboxInput()

class evaluacionesForm(forms.Form):
    MY_CHOICES = (
        ('Si', 'Si'),
        ('No', 'No'),
    )
    voto = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES)
    observacion = forms.CharField(widget=forms.Textarea)

class analisisLineaForm(forms.Form):
    MY_CHOICES = (
        ('Si', 'Si'),
        ('No', 'No'),
    )
    voto = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES)
    observacion = forms.CharField(widget=forms.Textarea)

from django import forms
from myapp.modulos.formulacion.models import Asignatura
from django.contrib.auth.models import Group

SEMESTRES = (('I','I'), ('II', 'II'))
SINO = ('Si', ' No')
ANOS = (('2014','2014'), ('2015', '2015'))



class crearProgramaForm(forms.Form):

	# asignaturas = [(c.id, c.nombreAsig) for c in Asignatura.objects.all()]
	# asignatura = forms.ChoiceField(required=True, label='Asignatura', choices=asignaturas)
	asignatura = forms.CharField(widget=forms.TextInput())
	semestre = forms.CharField(widget=forms.TextInput())
	ano = forms.CharField(widget=forms.TextInput())
	# semestre = forms.ChoiceField(choices=SEMESTRES)
	# ano = forms.ChoiceField(choices=ANOS)

	def clean(self):
		return self.cleaned_data

class estadoForm(forms.Form):
    MY_CHOICES = (
        ('opt0', 'Finalizado'),
        ('opt1', 'Modificando'),
    )
    estado = forms.ChoiceField(widget=forms.RadioSelect, choices=MY_CHOICES)

class definirObjetivosForm(forms.Form): 
	objetivos = forms.CharField(widget=forms.Textarea)

class definirCapacidadesForm(forms.Form): 
	capacidades = forms.CharField(widget=forms.Textarea)

class definirContenidosForm(forms.Form): 
	contenidos = forms.CharField(widget=forms.Textarea)

class definirClaseClaseForm(forms.Form): 
	claseclase  = forms.CharField(widget=forms.Textarea)

class definirCompletitudForm(forms.Form): 
	completitud  = forms.CharField(widget=forms.Textarea)

class decisionEvaluacionForm(forms.Form):
	decision = forms.ChoiceField(widget=forms.RadioSelect, choices=SINO)

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
	 	('Programacion de Actividades', (u"Programacion de Actividades")),
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
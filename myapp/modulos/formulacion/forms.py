
from django import forms

SEMESTRES = (('I','I'), ('II', 'II'))
SINO = ('Si', ' No')
ANOS = (('2014','2014'), ('2015', '2015'))



class crearProgramaForm(forms.Form):
	asignatura = forms.CharField(widget = forms.TextInput())
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
		('En General', (u"En General")),
		('Formulacion Programa por Linea', (u"Formulacion Programa por Linea")),
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
	title = forms.CharField(max_length=50)
	recurso = forms.FileField(label="Seleccione el archivo")
	descripcion = forms.CharField(widget=forms.Textarea)
	estado = forms.ChoiceField(choices=ESTADOS)
	
class LineasForm(forms.Form):
	nombreLinea  = forms.CharField(widget=forms.TextInput(),label="Nombre de Linea de Asignatura")
	# coordinador  = forms.CharField(widget=forms.Textarea)
	# profesor  = forms.CharField(widget=forms.Textarea)
 #    # TODO: Define form fields here


    # TODO: Define form fields here
    
	# asignatura = forms.CharField(widget = forms.TextInput())
	# semestre = forms.ChoiceField(widget=forms.RadioSelect, choices=SEMESTRES)
	# ano = forms.ChoiceField(widget=forms.RadioSelect, choices=ANOS)

class analizarForm(forms.Form):
	decision = forms.CheckboxInput()
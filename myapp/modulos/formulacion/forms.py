from django import forms

SEMESTRES = ('I', 'II')
SINO = ('Si', ' No')

class crearProgramaForm(forms.Form):
	asignatura = forms.CharField(widget = forms.TextInput())
	semestre = forms.CharField(widget = forms.TextInput())
	ano = forms.CharField(widget = forms.TextInput())

	def clean(self):
		return self.cleaned_data

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

	
class LineasForm(forms.Form):
	nombreLinea  = forms.CharField(widget=forms.TextInput(),label="Nombre de Linea de Asignatura")
	# coordinador  = forms.CharField(widget=forms.Textarea)
	# profesor  = forms.CharField(widget=forms.Textarea)
 #    # TODO: Define form fields here
class CoordinadorForm(forms.Form):

	coordinador  = forms.CharField(widget=forms.TextInput(), label='Ingrese Email del Coordinador')

    # TODO: Define form fields here
    
	# asignatura = forms.CharField(widget = forms.TextInput())
	# semestre = forms.ChoiceField(widget=forms.RadioSelect, choices=SEMESTRES)
	# ano = forms.ChoiceField(widget=forms.RadioSelect, choices=ANOS)

from django import forms

class CoordinadorForm(forms.Form):
	coordinador  = forms.CharField(widget=forms.TextInput(), label='Ingrese Email del Coordinador')
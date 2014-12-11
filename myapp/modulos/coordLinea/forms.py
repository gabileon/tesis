from django import forms

class CoordinadorForm(forms.Form):
	coordinador  = forms.CharField(widget=forms.TextInput(), label='Ingrese Email del Coordinador')

	def clean_email(self):
		if (self.cleaned_data.get('coordinador', '')
            .endswith('usach.cl')):
			raise ValidationError("Debes Ingresar un email del dominio USACH.")
		return self.cleaned_data.get('coordinador', '')
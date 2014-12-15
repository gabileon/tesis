from django import forms
from django.core.exceptions import ValidationError

class CoordinadorForm(forms.Form):
    coordinador  = forms.CharField(widget=forms.TextInput(), label='Ingrese Email del Coordinador')

    def clean_email(self):
        email = self.cleaned_data.get('coordinador')
        dominio =  email.split('@')[1]
        if (dominio != 'usach.cl'):

            raise ValidationError("Debes Ingresar un email del dominio USACH.")

       	super(CoordinadorForm, self).clean()
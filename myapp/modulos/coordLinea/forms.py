from django import forms
from django.core.exceptions import ValidationError

class CoordinadorForm(forms.Form):
    coordinador  = forms.CharField(widget=forms.TextInput(), label='Ingrese Email del Coordinador, recuerda que debe ser un email usach valido.')

    def clean_coordinador(self):
        email = self.cleaned_data.get('coordinador')
        dominio =  email.split('@')[1]
        if (dominio != 'usach.cl'):

            raise ValidationError("Debes Ingresar un email del dominio USACH.")

        return self.cleaned_data.get('coordinador', '')
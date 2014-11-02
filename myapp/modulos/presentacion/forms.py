from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label="Nombre de Usuario",widget=forms.TextInput())
    password = forms.CharField(label="Password",widget=forms.PasswordInput(render_value=False))

class RegisterForm(forms.Form):
	username = forms.CharField(label="Nombre de Usuario",widget=forms.TextInput())
	name = forms.CharField(label="Nombre",widget=forms.TextInput())
	last_name = forms.CharField(label="Apellido",widget=forms.TextInput())
	email = forms.EmailField(label="Correo Electronico", widget=forms.TextInput())
	password_one = forms.CharField(label="Password", widget=forms.PasswordInput(render_value=False))
	password_two = forms.CharField(label="Confirmar Password", widget=forms.PasswordInput(render_value=False))

class ImageUploadForm(forms.Form):
    image = forms.ImageField()

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from myapp.modulos.formulacion.models import Programa
from myapp.modulos.presentacion.models import UserProfile
from django.contrib.auth import authenticate, login, logout
from myapp.modulos.presentacion.forms import LoginForm, RegisterForm
from django.contrib.auth.models import User
# Create your views here.

def welcome_view(request):
	status = "GABRIELA"
	ctx = {'status' : status}
	return render(request, 'presentacion/welcome.html', ctx)

def programas_view(request):
	if request.method == "GET":
		programa = Programa.objects.all()
		#prod = producto.objects.filter(status=True) #Select "from ventas_productos where status = True"
		ctx = {'programas': programa}
		#return HttpResponse(programa)
		return render(request, 'presentacion/programas.html', ctx)

def cadaprograma_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	ctx = {'programa' : programa}
	return render(request, 'presentacion/ver_programa.html', ctx )

def signup_view(request):
	
	form = RegisterForm()
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			name = form.cleaned_data['name']
			last_name = form.cleaned_data['last_name']
			email = form.cleaned_data['email']
			password_one = form.cleaned_data['password_one']
			password_two = form.cleaned_data['password_two']
			newUser = User.objects.create_user(username=username, first_name=name, last_name=last_name, email=email, password=password_one)
			newUserProfile = UserProfile.objects.create(username=newUser, rol='JC')
			newUser.save()
			newUserProfile.save()

			return redirect('/login')
		else:
			ctx = {'form':form}
			return render(request,'presentacion/sign_up.html',ctx)
	ctx = {'form':form}
	return render(request,'presentacion/sign_up.html',ctx)

def login_view(request):
	status = ""
	if request.user.is_authenticated():
		return redirect('/programas') #Cambiar cuando este el estado disponible
	else:
		if request.method == "POST":
			form = LoginForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
				user = authenticate(username=username, password=password)
				if user is not None and user.is_active:
					login(request, user)
					
					userTemp = User.objects.get(username=request.user.username)
					perfilTemp = UserProfile.objects.get(username=userTemp.id)
					if (perfilTemp.rol =='JC'):
						# return HttpResponse("es jc")
						return HttpResponseRedirect('/principal_jc/')
					if (perfilTemp.rol =='CL'):
						return HttpResponseRedirect('/')
				else:
					status = "Usuario y/o Password incorrecto"
		else:
			form = LoginForm()
			ctx = {'form':form, 'status': status}
			return render(request,'presentacion/login.html',ctx)
	return render(request,'presentacion/login.html',ctx)


def logout_view(request):
	logout(request)
	return redirect('/login')

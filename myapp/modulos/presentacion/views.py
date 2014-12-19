from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from myapp.modulos.formulacion.models import Programa
from myapp.modulos.presentacion.models import UserProfile, CredentialsModel
from django.contrib.auth import authenticate, login, logout
from myapp.modulos.presentacion.forms import LoginForm, RegisterForm
from django.contrib.auth.models import User
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build
import httplib2
import os
from myapp import settings
import httplib2
# Create your views here.



CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive' ' https://www.googleapis.com/auth/calendar',
    redirect_uri=settings.REDIRECT_URI)

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
			newUser.save()
			newUserProfile = UserProfile.objects.create(user=newUser, rol_CL='CL')
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
		return redirect('/logout/') #Cambiar cuando este el estado disponible
	else:
		form = LoginForm()
		if request.method == "POST":
			form = LoginForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
				user = authenticate(username=username, password=password)
				if user is not None and user.is_active:
					login(request, user)
					FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,request.user)
					authorize_url = FLOW.step1_get_authorize_url()
					return HttpResponseRedirect(authorize_url)
				else:
					status = "Usuario y/o Password Incorrecto"
		ctx = {'form':form, 'status': status}
		return render(request,'presentacion/login.html',ctx)

def errorLoginView(request):
	user = User.objects.get(username=request.user.username)
	profile = UserProfile.objects.get(user=user)
	rol = profile.rol_actual
	return render(request,'presentacion/errorLogin.html',{'rol':rol, 'username': request.user.username})

def errorGoogleView(request):
	user = User.objects.get(username=request.user.username)
	profile = UserProfile.objects.get(user=user)
	rol = profile.rol_actual
	return render(request,'presentacion/errorGoogle.html',{'rol':rol, 'username': request.user.username})


def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

def oauth2_view(request):
	if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'],
                                 request.user):
		return  HttpResponseBadRequest()
	credential = FLOW.step2_exchange(request.REQUEST)
	storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
	storage.delete()
	storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
	storage.put(credential)
	userTemp = User.objects.get(username=request.user.username)
	perfilTemp = UserProfile.objects.get(user=userTemp.id)
	ctx = {'perfil': perfilTemp}
	return render(request,'presentacion/rol.html',ctx)

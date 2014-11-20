from django.shortcuts import render, redirect
import datetime, random, sha
from myapp.modulos.formulacion.forms import decisionEvaluacionForm, crearProgramaForm, definirObjetivosForm, definirCompletitudForm, definirCapacidadesForm, definirContenidosForm, definirClaseClaseForm
from myapp.modulos.formulacion.models import Programa, MyWorkflow, Objetivo, Capacidad, Contenido, ClaseClase, Completitud
from myapp.modulos.formulacion.forms import decisionEvaluacionForm, crearProgramaForm, definirObjetivosForm, definirCompletitudForm, definirCapacidadesForm, definirContenidosForm, definirClaseClaseForm
from myapp.modulos.indicadores.models import ProgramasPorEstado
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from myapp.modulos.presentacion.models import CredentialsModel
from myapp import settings
from django.contrib.auth.models import User
from myapp.modulos.presentacion.models import UserProfile
from datetime import datetime

from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build
import httplib2
import os


# Create your views here.



CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive',
    redirect_uri='http://localhost:8000/oauth2callback/')

def principalPLView(request):
	form = crearProgramaForm()
	username = request.user.username
	programas = Programa.objects.filter(profesorEncargado=request.user.id).order_by('-fechaUltimaModificacion')
	try:
		storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
		credential = storage.get()
		http= httplib2.Http()
		http= credential.authorize(http)
		drive_service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
	except:
		return redirect('/logout/')
	if request.method == "POST":
		userTemp = User.objects.get(username=request.user.username)
		perfilTemp = UserProfile.objects.get(user=userTemp.id)
		p = Programa()
		#p.to_formulacion()
		form = crearProgramaForm(request.POST)
		if form.is_valid():
			asignatura = form.cleaned_data['asignatura']
			semestre = form.cleaned_data['semestre']
			ano = form.cleaned_data['ano']
				### se crea programa
			p.asignatura = asignatura
			p.semestre = semestre
			p.ano = ano
			p.fechaUltimaModificacion = datetime.now()
			p.profesorEncargado = request.user
			p.save()
			titulo = "Programa " + asignatura + " " + semestre + " " + ano
			body = {
				'title':'%s'%(titulo),
				'mimeType': "application/vnd.google-apps.document",
				}						
			try:
				file = drive_service.files().insert(body=body).execute()
				url = file.get('alternateLink')
		 		p.url = url
		 		p.to_formulacion()
		 		p.to_datosAsig()
		 		p.save()
				try:
		 			x = ProgramasPorEstado.objects.get(estado=p.state.title)
		 		except ProgramasPorEstado.DoesNotExist:
		 		 	x = None
		 		if x is None:
		 			newIndicador = ProgramasPorEstado.objects.create(estado=p.state.title, cantidad=1)
		 		 	newIndicador.save()
		 		else:
		 			indicador = ProgramasPorEstado.objects.get(estado=p.state.title)
		 		 	indicador.cantidad = indicador.cantidad + 1
		 		 	indicador.save()		 		
			except:
	 			return render(request, 'comunicacion/error.html')
	else:
		form = crearProgramaForm()
				#GEt
	ctx = {'username' : username, 'form': form, 'programas': programas}
	return render(request, 'profLinea/principalPL.html', ctx)


	# try:
	# 	storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
	# 	credential = storage.get()
	# 	http = httplib2.Http()
	# 	http = credential.authorize(http)
	# 	drive_service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
	# except:
	# 	return redirect('/logout/')

	# if request.method == "POST":
	# 	userTemp = User.objects.get(username=request.user.username)
	# 	perfilTemp = UserProfile.objects.get(username=userTemp.id)
	# 	p = Programa()
	# 	#p.to_formulacion()
	# 	form = crearProgramaForm(request.POST)
	# 	if form.is_valid():
	# 			##si es valido, inicializo las variables

	# 		################ Comprobar que no tenga otra carpeta creada ############################
			
	# 		asignatura = form.cleaned_data['asignatura']
	# 		semestre = form.cleaned_data['semestre']
	# 		ano = form.cleaned_data['ano']
	# 		### se crea programa
	# 		p.asignatura = asignatura
	# 		p.semestre = semestre
	# 		p.ano = ano
	# 		p.fechaUltimaModificacion = datetime.now()
	# 		titulo = "Programa " + asignatura + " " + semestre + " " + ano
 	
	# 		## guardamos el programa
			
	# 		#### SI no existe carpeta ###
	# 		if(perfilTemp.carpeta is None):

	# 			try:
	# 				storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
	# 				credential = storage.get()
	# 				http = httplib2.Http()
	# 				http = credential.authorize(http)
	# 				drive_service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
	# 			except:
	# 				return redirect('vista_logout')

	# 			body = {
	# 				'title': 'Programas de Asignatura -'+request.user.first_name + " " + request.user.last_name,
	# 				'mimeType': "application/vnd.google-apps.folder"
	# 			}
	# 			### se crea carpeta ###

	# 			folder = drive_service.files().insert(body = body).execute()
	# 			id_folder = folder.get('id')
				
	# 			### Obtenemos el perfil y se agrega el id ####
	# 			userTemp = User.objects.get(username=request.user.username)
	# 			perfilTemp = UserProfile.objects.get(username=userTemp.id)
	# 			perfilTemp.carpeta = id_folder
	# 			perfilTemp.save()

	# 			body = {
	# 				'title':'%s'%(titulo),
	# 				'mimeType': "application/vnd.google-apps.document",
	# 				'parents' : [{'id' : perfilTemp.carpeta}]
	# 				}						
	# 			try:
	# 				file = drive_service.files().insert(body=body).execute()
	# 			except:
	# 				return render(request, 'comunicacion/error.html')
				
	# 		else:
	# 			#### si existe carpeta ###
	# 			body = {
	# 				'title':'%s'%(titulo),
	# 				'mimeType': "application/vnd.google-apps.document",
	# 				'parents' : [{'id' : perfilTemp.carpeta}]
	# 				}
	# 			#### se guarda documento en la carpeta ###			
	# 			try:
	# 				file = drive_service.files().insert(body=body).execute()
	# 			except:
	# 				return render(request, 'comunicacion/error.html')

	# 		url = file.get('alternateLink')
	# 		p.url = url
	# 		p.profesorEncargado = userTemp
	# 		p.to_formulacion()
	# 		p.to_datosAsig()
	# 		p.save()
	# 		objetivo = Objetivo(programa=p)
	# 		capacidad = Capacidad(programa=p)
	# 		contenido = Contenido(programa=p)
	# 		clase = ClaseClase(programa=p)
	# 		completitud = Completitud(programa=p)
	# 		objetivo.save()
	# 		capacidad.save()
	# 		contenido.save()
	# 		clase.save()
	# 		completitud.save()
	# 		ctx = {'form': form}
	# 		return HttpResponseRedirect("/principalPL/")
	# else:
	# 	#GEt
	# 	ctx = {'username' : username, 'form': form, 'programas': programas}
	# 	return render(request, 'profLinea/principalPL.html', ctx)

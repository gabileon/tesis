from django.shortcuts import render, redirect
import datetime, random, sha
from myapp.modulos.formulacion.forms import crearProgramaForm
from myapp.modulos.presentacion.forms import ImageUploadForm
from myapp.modulos.formulacion.models import Recurso, Analisis, AnalisisM, Log, Asignatura, Programa, MyWorkflow,  ClaseClase, Completitud
from myapp.modulos.jefeCarrera.models import Evento
from myapp.modulos.indicadores.models import ProgramasPorEstado
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from myapp.modulos.presentacion.models import CredentialsModel
from myapp import settings
from django.contrib.auth.models import User
from myapp.modulos.presentacion.models import UserProfile
from datetime import datetime
from myapp.modulos.presentacion.forms import cambiarDatosForm
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build
import httplib2
import os
from apiclient import errors


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive',
    redirect_uri='http://localhost:8000/oauth2callback/')

def cambiarDatosProfeView(request):
	form = cambiarDatosForm()
	user = request.user
	profile = UserProfile.objects.get(user=user)
	if request.method == "POST":
		form = cambiarDatosForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			last_name = form.cleaned_data['last_name']
			password = form.cleaned_data['password']
			user.first_name = name
			user.last_name = last_name
			user.set_password(password)
			user.save()
			profile.fechaPrimerAcceso = datetime.now()
			profile.save()
			redirect ('/miperfilProfesor/')
	ctx = {'form': form, 'username': request.user.username}
	return render(request, 'profLinea/cambiarDatos.html', ctx)

def miperfilProfesorView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            foto = form.cleaned_data['image']
            perfilTemp.foto = foto 
            perfilTemp.save()
            return redirect('/miperfilProfesor/')
    ctx = {'user': userTemp, 'perfil': perfilTemp, 'username': request.user.username}
    return render(request, 'profLinea/perfilConf.html', ctx)



def principalPLView(request):

	yo = User.objects.get(username=request.user.username)
	profile = UserProfile.objects.get(user=yo)
	if profile.fechaPrimerAcceso is None:
		return redirect('/cambiarDatosProfe/')

	programasApro = Programa.objects.filter(state='fin').filter(profesorEncargado=request.user).count()
	programas = Programa.objects.filter(state='aprobacionLinea')
	obtenerProgNo = []
	programasEval = Programa.objects.filter(state='analisisEvaluacionesAsociadas')
	estado = 5
	obtenerProgEvalNo = []
	for prog in programasEval:
		if prog.profesorEncargado != request.user:
			obtenerProgEvalNo.append(prog)
	finalesEval = []
	for p in obtenerProgNo:
		analisism = Evaluacion.objects.get(programa=p.id)
		try:
			votantesEval = Evaluaciones.objects.filter(evaluacion = analisism)
		except:
			votantesEval = 0
		if len(votantesEval)>0:
			estado = 2
			for v in votantesEval:
				##esta haciendo mal esta consulta
				if v.votante != yo:
					estado =3
					finalesEval.append(p)
		if len(votantesEval) == 0:
			estado = 4
			finalesEval.append(p)
	finEval = len(finalesEval)


	## obtengo los programas de ese estado que no son mios
	for prog in programas:
		try:
			if prog.profesorEncargado != request.user:
				obtenerProgNo.append(prog)
		except:
			fin = 0
	finales = []
	estado = 1
	votantes= []
	for p in obtenerProgNo:
		analisism = AnalisisM.objects.get(programa=p.id)
		try:
			votantes = Analisis.objects.filter(analisis = analisism)
		except:
			fin = len(obtenerProgNo)
		if len(votantes)>0:
			estado = 2
			for v in votantes:
				##esta haciendo mal esta consulta
				if v.votante != yo:
					estado =3
					finales.append(p)
	fin = len(finales)
	form = crearProgramaForm()
	username = request.user.username
	programas = Programa.objects.filter(profesorEncargado=request.user.id).order_by('-fechaUltimaModificacion')
	otrosProgramas = Programa.objects.all()
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
			asignaturaM = Asignatura.objects.get(id=asignatura)
			p.asignatura = asignaturaM
			p.semestre = semestre
			p.ano = ano
			p.fechaUltimaModificacion = datetime.now()
			p.profesorEncargado = request.user
			titulo = "Programa " + asignaturaM.nombreAsig + " " + semestre + " " + ano
			
			if (perfilTemp.carpetaProgramas == "NO CREADA"):
				### CREAMOS UNA CARPETA ###
				body = {
					'title': 'Programas de Asignatura -'+request.user.first_name + " " + request.user.last_name,
					'mimeType': "application/vnd.google-apps.folder"
				}
				### se crea carpeta ###

				folder = drive_service.files().insert(body = body).execute()
				id_folder = folder.get('id')
				perfilTemp.carpetaProgramas = id_folder

			body = {
				'title':'%s'%(titulo),
				'mimeType': "application/vnd.google-apps.document",
				'parents' : [{'id' : perfilTemp.carpetaProgramas}]
				}						
			try:
				file = drive_service.files().insert(body=body).execute()
				url = file.get('alternateLink')
		 		p.url = url
		 		p.to_formulacion()
		 		logEstado(p, p.state.title)
		 		p.to_datosAsig()
		 		logEstado(p, p.state.title)
		 		p.id_file = file['id']
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
	 			return redirect('/logout/')
	else:
		form = crearProgramaForm()
				#GEt
	ctx = { 'evaluaciones': finEval, 'username' : username,'estado': estado, 'finales' : fin, 'form': form, 'programas': programas, 'porAnalizar': fin, 'otros': otrosProgramas, 'aprobados': programasApro}
	return render(request, 'profLinea/principalPL.html', ctx)


def logEstado (programa, state):
	l= Log()
	l.programa = programa
	l.state = state
	l.fecha = datetime.now()
	l.save()	

def eliminarProgramaView(request, id_programa):
	try:
		storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
		credential = storage.get()
		http= httplib2.Http()
		http= credential.authorize(http)
		service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
	except:
		return redirect('/logout/')
	programa= Programa.objects.get(id=id_programa)
	try:
		service.files().delete(fileId=programa.id_file).execute()
	except errors.HttpError, error:
		print 'Ocurrio un error al eliminar el archivo %s' % error
		return redirect('/logout/')
	programa.delete()
	return redirect('/principalPL/')

def repositorioView(request):
	recursos = Recurso.objects.all()
	username = request.user.username
	ctx = {'recursos': recursos, 'username': username}
	return render(request, 'profLinea/recursos.html', ctx)

def fechasView(request):
	eventos = Evento.objects.all().filter(tipoEvento = 'profesor')
	username = request.user.username
	ctx = {'eventos': eventos, 'username': username}
	return render(request, 'profLinea/eventosProfe.html', ctx)
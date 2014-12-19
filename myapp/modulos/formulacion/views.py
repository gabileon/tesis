from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from myapp.modulos.formulacion.models import Evaluacion, Analisis, AnalisisM, Administrativo, RecursosApren, Linea, Profesor, Evaluaciones, Log, Programa, MyWorkflow, Recurso, Constribucion, RDA, Estrategias, ClaseClase, Completitud
from myapp.modulos.formulacion.forms import estadoForm, crearProgramaForm, evaluacionesForm, analisisLineaForm
from myapp.modulos.presentacion.models import UserProfile, CredentialsModel
from myapp import settings
from myapp.modulos.indicadores.models import ProgramasPorEstado
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build
from django.db.models import Q
import httplib2
import os
from google.appengine.api import mail

def logEstado (programa, state):
    l= Log()
    l.programa = programa
    l.state = state
    l.fecha = datetime.now() - timedelta(hours=3)
    l.save() 


########## PRIMER ESTADO ##############
def defGenerales(request, id_programa):
	### Obtenemos el perfil y se agrega el id ####
	programa = Programa.objects.get(id=id_programa)
	url = programa.url
	userTemp = User.objects.get(username=request.user.username)
	form = estadoForm()
	recursos = Recurso.objects.filter(estado=programa.state.title)
	if request.method == "POST":
	 	form = estadoForm(request.POST)
	 	choice = request.POST['optionsRadios']
	 	####### SI SE TERMINA LA DEFINICION ########
	 	if choice=='option2':
	 		y = ProgramasPorEstado.objects.get(estado=programa.state.title)
	 		y.cantidad = y.cantidad - 1
	 		y.save()
	 		programa.to_defGeneral()
	 		programa.fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
	 		logEstado(programa, programa.state.title)
	 		programa.save()
	 		try:
		 		x = ProgramasPorEstado.objects.get(estado=programa.state.title)
		 	except ProgramasPorEstado.DoesNotExist:
		 		 x = None
		 	if x is None:
		 		newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
		 	 	newIndicador.save()
		 	else:
		 		indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
		 	 	indicador.cantidad = indicador.cantidad + 1
		 	 	indicador.save()
		 	 	# SE INTENTA OBTENER CADA UNO DE LAS PARTES #
		 	 	### SE RESETEAN#
		 	try:
		 		ob = RDA.objects.get(programa = programa)
		 		rd = Estrategias.objects.get(programa=programa)
		 		con = Constribucion.objects.get(programa=programa)
		 		clase = ClaseClase.objects.get(programa=programa)
		 		compl = Completitud.objects.get(programa=programa)
		 		adm = Administrativo.objects.get(programa=programa)
		 		recursos = RecursosApren.objects.get(programa=programa)
		 		evaluacion = Evaluacion.objects.get(programa=programa)
		 		analisis = AnalisisM.objects.get(programa=programa)
		 		ob.estado = "Sin Iniciar"
		 		rd.estado = "Sin Iniciar"
		 		con.estado = "Sin Iniciar"
				compl.estado = "Sin Iniciar"
				clase.estado = "Sin Iniciar"
				adm.estado = "Sin Iniciar"
				recursos.estado = "Sin Iniciar"
	 			evaluacion.votoEvalCord = False
	 			evaluacion.votoProfe = False
	 			Evaluaciones.objects.filter(evaluacion=evaluacion).delete()
	 			evaluacion.save()
	 			analisis.votoEvalCord = False
	 			analisis.votoProfe = False
	 			Analisis.objects.filter(analisis=analisis).delete()
	 			analisis.save()
		 	except:
		 		# SI NO HAY, SE CREAN #
		 		ob = RDA()
		 		rd = Estrategias()
		 		con = Constribucion()
		 		clase = ClaseClase()
		 		compl = Completitud()
		 		adm = Administrativo()
		 		recursos = RecursosApren()
		 		evaluacion = Evaluacion()
		 		analisis = AnalisisM()
  			ob.programa = programa
  			rd.programa = programa
  			con.programa = programa
  			ob.save()
  			rd.save()
  			con.save()
  			clase.programa = programa
  			clase.save()
  			compl.programa = programa
  			compl.save()
  			adm.programa = programa
  			adm.save()
  			recursos.programa = programa
  			recursos.save()
  			evaluacion.programa = programa
  			evaluacion.save()
  			analisis.programa = programa
  			analisis.save()
  			return HttpResponseRedirect('/definiciones/'+id_programa)
 		else:
 			programa.fechaUltimaModificacion = datetime.now()-timedelta(hours=3)
	 		programa.save()
 			return HttpResponseRedirect('/principalPL/')
 	ctx = {'url': url, 'p': programa, 'form':form, 'recursos': recursos, 'username': request.user.username}
 	return render(request, 'formulacion/definicionesGenerales.html', ctx)
######  SEGUNDO ESTADO ######
def definicionesGeneralesAdmin(request, id_programa):
	user = User.objects.get(username= request.user.username)
	profile = UserProfile.objects.get(user = user)
	programa = Programa.objects.get(id=id_programa)
	rda = RDA.objects.get(programa=programa)
	estra = Estrategias.objects.get(programa=programa)
	clase = ClaseClase.objects.get(programa=programa)
	constribucion = Constribucion.objects.get(programa=programa)
	username=request.user.username
	if programa.state != 'definicionGeneral':
		programa.state = 'definicionGeneral'
		programa.save()
	ctx = {'p': programa, 'username': username, 'estadoClase': clase.estado, 'estadoRDA': rda.estado, 'estadoCons': constribucion.estado, 'estadoEstra': estra.estado}
	return render(request, 'formulacion/definiciones.html', ctx)
######  TERCCER ESTADO ######
def definicionConstribucion(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	constribucion = Constribucion.objects.get(programa=programa)
	if request.method == "GET":
		form = estadoForm()
		programa.to_defCons()
		programa.save()
		logEstado(programa, programa.state.title)
		
		if (constribucion.estado is not None):
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_defGeneralCons()
	 		programa.fechaUltimaModificacion = datetime.now()-timedelta(hours=3)
	 		logEstado(programa, programa.state.title)
	 		constribucion.estado = "Finalizado"
	 		constribucion.save()
	 		programa.save()
	 		return HttpResponseRedirect('/definiciones/'+id_programa)
		else:
	           ## guardamos el producto 
			constribucion.estado = "Modificando"
	 		constribucion.save()
			programa.to_defGeneralCons()
			programa.fechaUltimaModificacion =  datetime.now()-timedelta(hours=3)
			programa.save()	
	    	return HttpResponseRedirect('/definiciones/'+id_programa)
	
	ctx = {'form': form, 'p' : programa, 'form': form, 'username': request.user.username}
	return render(request, 'formulacion/definicionConstribucion.html', ctx)

def definicionRdA(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	definicion = RDA.objects.get(programa=programa)
	if request.method == "GET":
		form = estadoForm()
		programa.to_defRdA()
		programa.save()
		logEstado(programa, programa.state.title)
		
		if definicion.estado is not None:	
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_defGeneralRdA()
	 		programa.fechaUltimaModificacion =  datetime.now()-timedelta(hours=3)
	 		logEstado(programa, programa.state.title)
	 		definicion.estado = "Finalizado"
	 		definicion.save()
	 		programa.save()

		#programa.to_defObj()
		else:
	           ## guardamos el producto 
			definicion.estado = "Modificando"
	 		definicion.save()
			programa.to_defGeneralRdA()
			programa.fechaUltimaModificacion =  datetime.now()-timedelta(hours=3)
			programa.save()	
		return HttpResponseRedirect('/definiciones/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'form': form, 'username': request.user.username}
	return render(request, 'formulacion/definicionRdA.html', ctx)

def definicionEstra(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	definicion = Estrategias.objects.get(programa=programa)
	if request.method == "GET":
		form = estadoForm()
		programa.to_defEstrategias()
		programa.save()	
		logEstado(programa, programa.state.title)
		
		if definicion.estado is not None:
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_defGeneralEstra()
	 		programa.fechaUltimaModificacion =  datetime.now()-timedelta(hours=3)
	 		logEstado(programa, programa.state.title)
	 		definicion.estado = "Finalizado"
	 		definicion.save()
	 		programa.save()
		else:
	           ## guardamos el producto 
			definicion.estado = "Modificando"
	 		definicion.save()
			programa.to_defGeneralEstra()
			programa.fechaUltimaModificacion =  datetime.now()-timedelta(hours=3)
			programa.save()	
		return HttpResponseRedirect('/definiciones/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'username': request.user.username}
	return render(request, 'formulacion/definicionEstra.html', ctx)
######## CUARTO ESTADO #########
def definicionClaseClase_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	definicion = ClaseClase.objects.get(programa=programa)
	if request.method == "GET":
		form = estadoForm()
		programa.to_defCons()
		programa.to_defClase()
		logEstado(programa, programa.state.title)
		programa.save()	
		if definicion.estado is not None:
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_analisisEval()
	 		programa.fechaUltimaModificacion =  datetime.now()-timedelta(hours=3)
	 		logEstado(programa, programa.state.title)
	 		definicion.estado = "Finalizado"
	 		definicion.save()
	 		programa.save()
	 		return HttpResponseRedirect('/evaluacionesAsociadas/'+id_programa)
		else:
	           ## guardamos el producto 
			definicion.estado = "Modificando"
	 		definicion.save()
			programa.to_defGeneralClase()
			programa.fechaUltimaModificacion =  datetime.now()-timedelta(hours=3)
			programa.save()	
			return HttpResponseRedirect('/definiciones/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'form': form, 'username': request.user.username}
	return render(request, 'formulacion/definicionClaseClase.html', ctx)

#### QUINTO ESTADO #####
####### ANALISIS EVALUACIONES ASOCIADAS POR EL PROFESOR ENCARGADO########
def evaluacionesAsociadasView(request, id_programa):
	form = evaluacionesForm()
	programa = Programa.objects.get(id=id_programa)
	profe = programa.profesorEncargado
	linea = Profesor.objects.get(user = profe).linea
	coordinadorLinea = linea.coordinador
	profesoresLinea = Profesor.objects.filter(linea=linea).count()
	evaluacion = Evaluacion.objects.get(programa=programa)
	### ver si voto el profe ##
	if evaluacion.votoProfe == True:
		estado = 1
	else:
		estado = 0
	if evaluacion.votoEvalCord == True:
		cord = 1
	else:
		cord = 0
	votos = Evaluaciones.objects.filter(evaluacion =evaluacion)
	nvotos = Evaluaciones.objects.filter(evaluacion =evaluacion).count()

	if (nvotos == profesoresLinea + 1):
		bandera = evaluacionesVot(evaluacion)

	if estado == 0:
		if request.method == 'POST':
			form = evaluacionesForm(request.POST)
			if form.is_valid():
				voto = form.cleaned_data['voto']
				observacion = form.cleaned_data['observacion']
				votante = request.user
				eva = Evaluaciones.objects.create(voto = voto, observacion=observacion, votante=votante, evaluacion=evaluacion)
				eva.save()
				evaluacion.votoProfe = True
				evaluacion.save()
				return redirect('/principalPL')
	ctx = {'form': form, 'p' : programa, 'votos': votos, 'username': request.user.username, 'estado':estado, 'numvotos': profesoresLinea}
	return render(request, 'formulacion/evaluacionAsociadaOwn.html', ctx)

## PROCESO DE VOTACION ####
def evaluacionesVot(evaluacion):
	profe = evaluacion.programa.profesorEncargado
	termino = 0
	bandera = None
	programa = evaluacion.programa
	votos = Evaluaciones.objects.filter(evaluacion =evaluacion)
	numVotos = len(votos)
	linea = Profesor.objects.get(user = profe).linea
	coordinadorLinea = linea.coordinador
	profesoresLinea = Profesor.objects.filter(linea=linea).count()
	##### Termino la votacion #######
	if (numVotos == (profesoresLinea+1 )):
		termino = 1
		#### conteo de votos ###
		votosSi = votos.filter(voto='Si').count()
		votosNo =  votos.filter(voto='No').count()
		################# Resultados ###########
		if votosSi>votosNo :
			programa.siEvaluacion_toVerif()
			logEstado(programa, programa.state.title)
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()
			programa.save()
			bandera = True
		if votosSi<votosNo:
			bandera = True
			programa.noEvaluacion_toForm()
			logEstado(programa, programa.state.title)
			programa.to_datosAsig()
			programa.save()
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()
		if votosNo==votosSi:
			## veo el voto del coordinador
			votoDelCoord = Evaluaciones.objects.filter(evaluacion=evaluacion).get(votante = coordinadorLinea)
			if votoDelCoord == 'Si':
				perdieron = 0
				programa.siEvaluacion_toVerif()
				logEstado(programa, programa.state.title)
				try:
					x = ProgramasPorEstado.objects.get(estado=programa.state.title)
				except ProgramasPorEstado.DoesNotExist:
					x = None
				if x is None:
					newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
				 	newIndicador.save()
				else:
					indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
					indicador.cantidad = indicador.cantidad + 1
					indicador.save()
				programa.save()
				bandera = True
			else:
				bandera = False
				perdieron = 1
				programa.noEvaluacion_toForm()
				logEstado(programa, programa.state.title)
				programa.to_datosAsig()
				programa.save()
				try:
					x = ProgramasPorEstado.objects.get(estado=programa.state.title)
				except ProgramasPorEstado.DoesNotExist:
					x = None
				if x is None:
					newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
				 	newIndicador.save()
				else:
					indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
					indicador.cantidad = indicador.cantidad + 1
					indicador.save()
	else:
		termino = 0
	return bandera

def evaluacionesAsociadasOthersView(request):
	programasEval = Programa.objects.filter(state='analisisEvaluacionesAsociadas').filter(~Q(profesorEncargado=request.user))
	estado = 5
	yo = User.objects.get(username = request.user.username)
	finales = []
	for p in programasEval:
		analisism = Evaluacion.objects.get(programa=p.id)
		try:
			votantes = Evaluaciones.objects.filter(evaluacion = analisism).filter(~Q(votante=request.user))
		except:
			votantes = 0
		if votantes !=0:
			finales.append(p)
	if len(finales) == 0:
		finales = programasEval
	form = evaluacionesForm()  
	ctx = {'username': request.user.username, 'programas': finales, 'form': form,  'yo': estado}
	return render (request, 'formulacion/evaluacionAsociadaOther.html', ctx)



def votacionEvaluacionOtroProfeView(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	analisis = programa.evaluacion
	if request.method == 'POST':
		form = evaluacionesForm(request.POST)
		if form.is_valid():
			voto = form.cleaned_data['voto']
			observacion = form.cleaned_data['observacion']
			votante = request.user
			eva = Evaluaciones.objects.create(voto = voto, observacion=observacion, votante=votante, evaluacion=analisis)
			eva.save()
			evaluacionesVot(analisis)
			return redirect('/principalPL/')

####### FIN ###########



def definicionCompletitudCoherencia_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	definicion = Completitud.objects.get(programa=programa)
	if request.method == "GET":
		form = estadoForm()
		if definicion.estado is not None:
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.verificacion_toAspectosFinal()
	 		programa.fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
	 		logEstado(programa, programa.state.title)
	 		definicion.estado = "Finalizado"
	 		definicion.save()
	 		programa.save()
	 		return HttpResponseRedirect('/intermedioAdmRec/'+id_programa)
		else:
	           ## guardamos el producto 
			definicion.estado = "Modificando"
	 		definicion.save()
			programa.fechaUltimaModificacion = datetime.now()  - timedelta(hours=3)
			programa.save()	
			return HttpResponseRedirect('/principalPL/')
	ctx = {'form': form, 'p' : programa, 'form': form, 'username': request.user.username}
	return render(request, 'formulacion/completitud.html', ctx)

def intermedioAdmRecView (request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	username=request.user.username
	adm = Administrativo.objects.get(programa=programa)
	rec = RecursosApren.objects.get(programa=programa)
	if programa.state != 'definicionAspectosFinales':
		programa.state = 'definicionAspectosFinales'
		programa.save()
	if adm.estado == 'Finalizado' and rec.estado=='Finalizado':
		programa.to_defAspectos()
		programa.to_aprobPrograma()
		programa.save()
	ctx = {'p': programa, 'username': username, 'estadoAdm': adm.estado, 'estadoRec': rec.estado}
	return render(request, 'formulacion/aspectosFinales.html', ctx)

def aspectosAdm_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	definicion = Administrativo.objects.get(programa=programa)
	if request.method == "GET":
		programa.to_defAspectos()
		form = estadoForm()
		if definicion.estado is not None:
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_AdmAspectos()
	 		programa.fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
	 		logEstado(programa, programa.state.title)
	 		definicion.estado = "Finalizado"
	 		definicion.save()
	 		programa.save()
	 		return HttpResponseRedirect('/intermedioAdmRec/'+id_programa)
		else:
	           ## guardamos el producto 
			definicion.estado = "Modificando"
	 		definicion.save()
	 		programa.to_AdmAspectos()
			programa.fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
			programa.save()	
			return HttpResponseRedirect('/intermedioAdmRec/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'form': form, 'username': request.user.username}
	return render(request, 'formulacion/aspecAdm.html', ctx)

def recursosAprend_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	definicion = RecursosApren.objects.get(programa=programa)
	if request.method == "GET":
		programa.to_defRecursos()
		form = estadoForm()
		if definicion.estado is not None:
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_RecAspectos()
	 		programa.fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
	 		definicion.estado = "Finalizado"
	 		definicion.save()
	 		programa.save()
	 		return HttpResponseRedirect('/intermedioAdmRec/'+id_programa)
		else:
	           ## guardamos el producto 
			definicion.estado = "Modificando"
	 		definicion.save()
	 		programa.to_RecAspectos()
	 		logEstado(programa, programa.state.title)
			programa.fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
			programa.save()	
			return HttpResponseRedirect('/intermedioAdmRec/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'form': form, 'username': request.user.username}
	return render(request, 'formulacion/recursosAprendizaje.html', ctx)



##### FastTrack por el coordinador ###
def fastTrackDecisionView(request, id_programa, decision):
	programa = Programa.objects.get(id=id_programa)
	
	if decision == 'yes':        
		try:
			x = ProgramasPorEstado.objects.get(estado=programa.state.title)
		except ProgramasPorEstado.DoesNotExist:
			x = None
		if x is None:
			newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			newIndicador.save()
		else:
			x.cantidad = x.cantidad - 1
			x.save()
			programa.siFT_toAprobJC()
			logEstado(programa, programa.state.title)
			programa.save()
			try:
				y = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				y = None
			if y is None:
				newIndicador2 = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
				newIndicador2.save()
			else:
				y.cantidad = y.cantidad + 1
				y.save()
	if decision == 'no':
		try:
			m = ProgramasPorEstado.objects.get(estado=programa.state.title)
		except ProgramasPorEstado.DoesNotExist:
			m = None
		if m is None:
			newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			newIndicador.save()
        if m is not None:
            m.cantidad = m.cantidad - 1
            m.save()
            programa.noFT_toAnalisisJC()
            logEstado(programa, programa.state.title)
            programa.save()
            try:
                n = ProgramasPorEstado.objects.get(estado=programa.state.title)
            except ProgramasPorEstado.DoesNotExist:
                n = None
            if n is None:
                newIndicador2 = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
                newIndicador2.save()
            else:
                n.cantidad = m.cantidad + 1
                n.save()
            return HttpResponseRedirect('/principal_cl/')

### FUNCION DE ANALISIS ###
def analisisVot(evaluacion):
	profe = evaluacion.programa.profesorEncargado
	termino = 0
	bandera = None
	programa = evaluacion.programa
	votos = Analisis.objects.filter(analisis =evaluacion)
	numVotos = len(votos)
	linea = Profesor.objects.get(user = profe).linea
	coordinadorLinea = linea.coordinador
	profesoresLinea = Profesor.objects.filter(linea=linea).count()
	##### Termino la votacion #######
	if (numVotos == (profesoresLinea+1 )):
		termino = 1
		#### conteo de votos ###
		votosSi = votos.filter(voto='Si').count()
		votosNo =  votos.filter(voto='No').count()
		################# Resultados ###########
		if votosSi>votosNo :
			programa.siAprob_toFT()
			logEstado(programa, programa.state.title)
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()
			programa.save()
			bandera = True
		if votosSi<votosNo:
			bandera = True
			programa.noAprob_toForm()
			programa.contador= programa.contador + 1
			logEstado(programa, programa.state.title)
			programa.to_datosAsig()
			programa.save()
			try:
				x = ProgramasPorEstado.objects.get(estado=programa.state.title)
			except ProgramasPorEstado.DoesNotExist:
				x = None
			if x is None:
				newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
			 	newIndicador.save()
			else:
				indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
				indicador.cantidad = indicador.cantidad + 1
				indicador.save()
		if votosNo==votosSi:
			## veo el voto del coordinador
			votoDelCoord = Analisis.objects.filter(evaluacion=evaluacion).get(votante = coordinadorLinea)
			if votoDelCoord == 'Si':
				perdieron = 0
				programa.siAprob_toFT()
				logEstado(programa, programa.state.title)
				try:
					x = ProgramasPorEstado.objects.get(estado=programa.state.title)
				except ProgramasPorEstado.DoesNotExist:
					x = None
				if x is None:
					newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
				 	newIndicador.save()
				else:
					indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
					indicador.cantidad = indicador.cantidad + 1
					indicador.save()
				programa.save()
				bandera = True
			else:
				bandera = False
				perdieron = 1
				programa.noAprob_toForm()
				programa.contador= programa.contador + 1
				logEstado(programa, programa.state.title)
				programa.to_datosAsig()
				programa.save()
				try:
					x = ProgramasPorEstado.objects.get(estado=programa.state.title)
				except ProgramasPorEstado.DoesNotExist:
					x = None
				if x is None:
					newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
				 	newIndicador.save()
				else:
					indicador = ProgramasPorEstado.objects.get(estado=programa.state.title)
					indicador.cantidad = indicador.cantidad + 1
					indicador.save()
	else:
		termino = 0
	return bandera


#### Votacion propia de aprobacion del programa ####
def votacionAnalisisProfeView(request, id_programa):
	form = analisisLineaForm()
	programa = Programa.objects.get(id=id_programa)
	profe = programa.profesorEncargado
	linea = Profesor.objects.get(user = profe).linea
	coordinadorLinea = linea.coordinador
	profesoresLinea = Profesor.objects.filter(linea=linea).count()
	evaluacion = AnalisisM.objects.get(programa=programa)
	### ver si voto el profe $$
	if evaluacion.votoProfe == True:
		estado = 1
	else:
		estado = 0
	if evaluacion.votoEvalCord == True:
		cord = 1
	else:
		cord = 0
	votos = Analisis.objects.filter(analisis =evaluacion)
	nvotos = Analisis.objects.filter(analisis =evaluacion).count()

	if (nvotos == profesoresLinea + 1):
		bandera = evaluacionesVot(evaluacion)

	if estado == 0:
		if request.method == 'POST':
			form = analisisLineaForm(request.POST)
			if form.is_valid():
				voto = form.cleaned_data['voto']
				observacion = form.cleaned_data['observacion']
				votante = request.user
				eva = Analisis.objects.create(voto = voto, observacion=observacion, votante=votante, analisis=evaluacion)
				eva.save()
				evaluacion.votoProfe = True
				evaluacion.save()
				return redirect('/principalPL/')
	ctx = {'form': form, 'p' : programa, 'votos': votos, 'username': request.user.username, 'estado':estado, 'numvotos': nvotos}
	return render(request, 'formulacion/analisisProgramaOwn.html', ctx)

######### Votacion de los otros profes aprobacion ######
def votacionAnalisisOtroProfeView(request):
	### obtengo todos los programas qe estan en ese estado
	programasEval = Programa.objects.filter(state='aprobacionLinea').filter(~Q(profesorEncargado=request.user))
	estado = 5
	yo = User.objects.get(username = request.user.username)
	finales = []
	for p in programasEval:
		analisism = AnalisisM.objects.get(programa=p.id)
		try:
			votantes = Analisis.objects.filter(evaluacion = analisism).filter(~Q(votante=request.user))
		except:
			votantes = 0
		if votantes !=0:
			finales.append(p)
	if len(finales) == 0:
		finales = programasEval
	form = analisisLineaForm()  
	ctx = {'username': request.user.username, 'programas': finales, 'form': form, }
	return render (request, 'formulacion/analisisProgramaOther.html', ctx)


def votacionOtroProfeView(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	analisis = programa.analisism
	if request.method == 'POST':
		form = analisisLineaForm(request.POST)
		if form.is_valid():
			voto = form.cleaned_data['voto']
			observacion = form.cleaned_data['observacion']
			votante = request.user
			eva = Analisis.objects.create(voto = voto, observacion=observacion, votante=votante, analisis=analisis)
			eva.save()
			analisisVot(analisis)
			return redirect('/principalPL/')

def fastTrackOwnView(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	return render(request, 'formulacion/ft.html', {'programa': programa, 'username': request.user.username,})


def analisisProgramaJCView(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	return render(request, 'formulacion/analisisJC.html', {'programa': programa, 'username': request.user.username,})

def aprobacionProgramaJCView(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	return render(request, 'formulacion/aprobacionJC.html', {'programa': programa, 'username': request.user.username,})


def buscarEstado(request, id_programa, estado):
	if (estado == 'definicionDatosAsignatura' ):
		return HttpResponseRedirect('/definicionesGenerales/'+id_programa)
	if (estado == 'definicionGeneral'):
		return HttpResponseRedirect('/definiciones/'+id_programa)
	if (estado == 'definicionConstribucion' ):
	 	return HttpResponseRedirect('/definicionConstribucion/'+id_programa )
	if (estado == 'definicionRdA' ):
	 	return HttpResponseRedirect('/definicionRdA/'+id_programa)
	if (estado == 'definicionEstrategias' ):
	 	return HttpResponseRedirect('/definicionEstrategias/'+id_programa)
	if (estado == 'definicionClaseClase' ):
	 	return HttpResponseRedirect('/definicionClaseClase/'+id_programa)
	if (estado == 'analisisEvaluacionesAsociadas' ):
	 	return HttpResponseRedirect('/evaluacionesAsociadas/'+id_programa)
	if (estado == 'verificacionCoherenciaCompletitud'):
	 	return HttpResponseRedirect('/definicioncoherenciacompletitud/'+id_programa)
	if (estado == 'definicionAspecAdmin' ):
	 	return HttpResponseRedirect('/aspectosAdm/'+id_programa)
	if (estado ==  'definicionRecursos' ):
	 	return HttpResponseRedirect('/recursosAprend/'+id_programa)
	if (estado ==  'definicionAspectosFinales' ):
	 	return HttpResponseRedirect('/intermedioAdmRec/'+id_programa)
	if (estado == 'aprobacionLinea' ):
	 	return HttpResponseRedirect('/votacionAnalisisProfe/'+id_programa)
	if (estado == 'fastTrack' ):
		return HttpResponseRedirect('/fastTrackOwn/'+id_programa)
	if (estado == 'analisisProgramaJC' ):
	 	return HttpResponseRedirect('/analisisProgramaJC/'+id_programa)
	if (estado == 'aprobacionProgramaJC'):
		return HttpResponseRedirect('/aprobacionProgramaJC/'+id_programa)

	


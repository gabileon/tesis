from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from datetime import datetime
from myapp.modulos.formulacion.models import Administrativo, RecursosApren, Linea, Profesor, Evaluaciones, Log, Programa, MyWorkflow, Recurso, Constribucion, RDA, Estrategias, ClaseClase, Completitud
from myapp.modulos.formulacion.forms import estadoForm, crearProgramaForm, evaluacionesForm, analisisLineaForm
from myapp.modulos.presentacion.models import CredentialsModel
from myapp import settings
from myapp.modulos.indicadores.models import ProgramasPorEstado
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build
import httplib2
import os
from google.appengine.api import mail

def logEstado (programa, state):
    l= Log()
    l.programa = programa
    l.state = state
    l.fecha = datetime.now()
    l.save() 

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
	 	if choice=='option2':
	 		y = ProgramasPorEstado.objects.get(estado=programa.state.title)
	 		y.cantidad = y.cantidad - 1
	 		y.save()
	 		programa.to_defGeneral()
	 		programa.fechaUltimaModificacion = datetime.utcnow()
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
  			ob = RDA()
  			ob.programa = programa
  			rd = Estrategias()
  			rd.programa = programa
  			con = Constribucion()
  			con.programa = programa
  			ob.save()
  			rd.save()
  			con.save()
  			clase = ClaseClase()
  			clase.programa = programa
  			clase.save()
  			compl = Completitud()
  			compl.programa = programa
  			compl.save()
  			adm = Administrativo()
  			adm.programa = programa
  			adm.save()
  			recursos = RecursosApren()
  			recursos.programa = programa
  			recursos.save()
  			return HttpResponseRedirect('/definiciones/'+id_programa)

 		else:
 			programa.fechaUltimaModificacion = datetime.utcnow()
	 		programa.save()
 			return HttpResponseRedirect('/principalPL/')
 	ctx = {'url': url, 'p': programa, 'form':form, 'recursos': recursos, 'username': request.user.username}
 	return render(request, 'formulacion/definicionesGenerales.html', ctx)

def definicionesGeneralesAdmin(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	username=request.user.username
	constribucion = Constribucion.objects.get(programa=programa)
	rda = RDA.objects.get(programa=programa)
	estra = Estrategias.objects.get(programa=programa)
	clase = ClaseClase.objects.get(programa=programa)
	if programa.state != 'definicionGeneral':
		programa.state = 'definicionGeneral'
		programa.save()
	ctx = {'p': programa, 'username': username, 'estadoClase': clase.estado, 'estadoRDA': rda.estado, 'estadoCons': constribucion.estado, 'estadoEstra': estra.estado}
	return render(request, 'formulacion/definiciones.html', ctx)

def definicionConstribucion(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	constribucion = Constribucion.objects.get(programa=programa)
	if request.method == "GET":
		form = estadoForm()
		programa.to_defCons()
		logEstado(programa, programa.state.title)
		programa.save()
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
	 		programa.fechaUltimaModificacion = datetime.now()
	 		
	 		constribucion.estado = "Finalizado"
	 		constribucion.save()
	 		programa.save()
	 		 		
	 		return HttpResponseRedirect('/definiciones/'+id_programa)
		#programa.to_defObj()
		else:
	           ## guardamos el producto 
			constribucion.estado = "Modificando"
	 		constribucion.save()
			programa.to_defGeneralCons()
			programa.fechaUltimaModificacion = datetime.now()
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
	 		programa.to_defGeneralRdA()
	 		programa.fechaUltimaModificacion = datetime.now()
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
			programa.fechaUltimaModificacion = datetime.now()
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
	 		programa.to_defGeneralEstra()
	 		programa.fechaUltimaModificacion = datetime.now()
	 		logEstado(programa, programa.state.title)
	 		definicion.estado = "Finalizado"
	 		definicion.save()
	 		programa.save()

		#programa.to_defObj()
		else:
	           ## guardamos el producto 
			definicion.estado = "Modificando"
	 		definicion.save()
			programa.to_defGeneralEstra()
			programa.fechaUltimaModificacion = datetime.now()
			programa.save()	
		return HttpResponseRedirect('/definiciones/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'username': request.user.username}
	return render(request, 'formulacion/definicionEstra.html', ctx)

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
	 		programa.fechaUltimaModificacion = datetime.now()
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
			programa.fechaUltimaModificacion = datetime.now()
			programa.save()	
			return HttpResponseRedirect('/definiciones/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'form': form, 'username': request.user.username}
	return render(request, 'formulacion/definicionClaseClase.html', ctx)

def evaluacionesAsociadasView(request, id_programa):
	
	form = evaluacionesForm()

	programa = Programa.objects.get(id=id_programa)
	form = evaluacionesForm()
	profe = programa.profesorEncargado
	linea = Profesor.objects.get(user = profe).linea
	coordinadorLinea = linea.coordinador
	profesoresLinea = Profesor.objects.filter(linea=linea).count()
	votos = Evaluaciones.objects.filter(programa=programa)
	perdieron = 0
	termino = 0
	estadoMiVoto = 'no'
	try:
		voteYo = Evaluaciones.objects.filter(programa=programa).get(votante=profe)
	except:
		voteYo = None
	if voteYo is not None:
		voteYo = 1
	else:
		voteYo = 0
	## ver si voto el coordinador ##
	try:
		votoCoord = Evaluaciones.objects.get(votante=coordinadorLinea)
	except:
		votoCoord = 0
	if votoCoord is None:
		votoCoord = 1
	else:
		votoCoord = 0

	## form ###
	# try:
	#  	votos = Evaluaciones.objects.filter(programa=programa)
	 	
	# except:
	#  	votos = None

	if len(votos) != 0 :
		numVotos = Evaluaciones.objects.filter(programa=programa).count()
		
		if numVotos == (profesoresLinea + 1):
			## todos votaron
			termino = 1
			votosSi = votos.filter(voto='Si').count()
			votosNo =  votos.filter(voto='No').count()
			if votosSi>votosNo :

				## si hay evaluaciones
				## se envia email al profe y al coordinador
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
				### envio el email al coordinador y al profeEncargado
				# message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
    #         	message.to = coordinadorLinea.email
    #             message.html """"
				# 			<html><head></head><body>
				# 			Estimado:

				# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
				# 			Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , ha sido exitosa
				# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
				# 			Saludos
				# 			</body></html>
				# 		"""%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

    #             message.send()
    #             message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
    #         	message.to = profe.email
    #             message.html """"
				# 			<html><head></head><body>
				# 			Estimado:

				# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
				# 			Asociadas a lo definido en el programa de asignatura %s %s %s, ha sido exitosa
				# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
				# 			Saludos
				# 			</body></html>
				# 		"""%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

    #             message.send()
				programa.save()

			if votosSi<votosNo:
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

				#message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
      #       	message.to = coordinadorLinea.email
      #           message.html """"
						# 	<html><head></head><body>
						# 	Estimado:

						# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
						# 	Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , no ha sido exitosa
						# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
						# 	Saludos
						# 	</body></html>
						# """%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

      #           message.send()
      #           message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
      #       	message.to = profe.email
      #           message.html """"
						# 	<html><head></head><body>
						# 	Estimado:

						# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
						# 	Asociadas a lo definido en el programa de asignatura %s %s %s, no ha sido exitosa
						# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
						# 	Saludos.




						# 	</body></html>
						# """%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

      #           message.send()
			if votosNo==votosSi:
				## veo el voto del coordinador
				votoDelCoord = Evaluaciones.objects.filter(programa = id_programa).get(votante = coordinadorLinea)
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
					### envio el email al coordinador y al profeEncargado
				# message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
    #         	message.to = coordinadorLinea.email
    #             message.html """"
				# 			<html><head></head><body>
				# 			Estimado:

				# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
				# 			Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , ha sido exitosa
				# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
				# 			Saludos
				# 			</body></html>
				# 		"""%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

    #             message.send()
    #             message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
    #         	message.to = profe.email
    #             message.html """"
				# 			<html><head></head><body>
				# 			Estimado:

				# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
				# 			Asociadas a lo definido en el programa de asignatura %s %s %s, ha sido exitosa
				# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
				# 			Saludos
				# 			</body></html>
				# 		"""%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

    #             message.send()

					programa.save()
				else:
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

					#message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
	      #       	message.to = coordinadorLinea.email
	      #           message.html """"
							# 	<html><head></head><body>
							# 	Estimado:

							# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
							# 	Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , no ha sido exitosa
							# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
							# 	Saludos
							# 	</body></html>
							# """%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

	      #           message.send()
	      #           message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
	      #       	message.to = profe.email
	      #           message.html """"
							# 	<html><head></head><body>
							# 	Estimado:

							# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
							# 	Asociadas a lo definido en el programa de asignatura %s %s %s, no ha sido exitosa
							# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
							# 	Saludos.




							# 	</body></html>
							# """%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

	      #           message.send()
						
					## PErdieorn
		else:
			termino = 0
	if request.method == 'POST':
		form = evaluacionesForm(request.POST)
		if form.is_valid():
			voto = form.cleaned_data['voto']
			observacion = form.cleaned_data['observacion']
			votante = request.user
			evaluacion = Evaluaciones.objects.create(voto = voto, observacion=observacion, votante=votante, programa=programa)
			evaluacion.save()
			return HttpResponseRedirect('/evaluacionesAsociadas/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'username': request.user.username, 'votos': votos, 'estado': voteYo, 'termino':termino, 'perdieron': perdieron}
	return render(request, 'formulacion/evaluacionAsociadaOwn.html', ctx)

def evaluacionesAsociadasOthersView(request, id_programa):
	form = evaluacionesForm()

	programa = Programa.objects.get(id=id_programa)
	form = evaluacionesForm()
	profe = programa.profesorEncargado
	profeV =request.user
	linea = Profesor.objects.get(user = profe).linea
	
	try:
		voteYo = Evaluaciones.objects.get(votante=profeV.id)
	except:
		voteYo = None
	if voteYo is not None:
		voteYo = 0
	else:
		voteYo = 1
	## ver si voto el coordinador ##
	try:
		votoCoord = Evaluaciones.objects.get(votante=coordinadorLinea)
	except:
		votoCoord = 0
	if votoCoord is None:
		votoCoord = 0
	else:
		votoCoord = 1
	
	if request.method == 'POST':
		form = evaluacionesForm(request.POST)
		if form.is_valid():
			voto = form.cleaned_data['voto']
			observacion = form.cleaned_data['observacion']
			votante = request.user
			evaluacion = Evaluaciones.objects.create(voto = voto, observacion=observacion, votante=votante, programa=programa)
			evaluacion.save()
			return HttpResponseRedirect('/principalPL/')
			profesoresLinea = Profesor.objects.filter(linea=linea).count()
			coordinadorLinea = linea.coordinador
			votos = Evaluaciones.objects.filter(programa=programa)
			perdieron = 0
			termino = 0
			estadoMiVoto = 'no'
			if len(votos) != 0 :
				numVotos = Evaluaciones.objects.filter(programa=programa).count()
				if numVotos == (profesoresLinea + 1):
					## todos votaron
					termino = 1
					votosSi = votos.filter(voto='Si').count()
					votosNo =  votos.filter(voto='No').count()
					if votosSi>votosNo :

						## si hay evaluaciones
						## se envia email al profe y al coordinador
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
						### envio el email al coordinador y al profeEncargado
						# message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
		    #         	message.to = coordinadorLinea.email
		    #             message.html """"
						# 			<html><head></head><body>
						# 			Estimado:

						# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
						# 			Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , ha sido exitosa
						# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
						# 			Saludos
						# 			</body></html>
						# 		"""%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

		    #             message.send()
		    #             message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
		    #         	message.to = profe.email
		    #             message.html """"
						# 			<html><head></head><body>
						# 			Estimado:

						# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
						# 			Asociadas a lo definido en el programa de asignatura %s %s %s, ha sido exitosa
						# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
						# 			Saludos
						# 			</body></html>
						# 		"""%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

		    #             message.send()
						programa.save()

					if votosSi<votosNo:
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

						#message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
		      #       	message.to = coordinadorLinea.email
		      #           message.html """"
								# 	<html><head></head><body>
								# 	Estimado:

								# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
								# 	Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , no ha sido exitosa
								# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
								# 	Saludos
								# 	</body></html>
								# """%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

		      #           message.send()
		      #           message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
		      #       	message.to = profe.email
		      #           message.html """"
								# 	<html><head></head><body>
								# 	Estimado:

								# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
								# 	Asociadas a lo definido en el programa de asignatura %s %s %s, no ha sido exitosa
								# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
								# 	Saludos.




								# 	</body></html>
								# """%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

		      #           message.send()
					if votosNo==votosSi:
						## veo el voto del coordinador
						votoDelCoord = Evaluaciones.objects.filter(programa = id_programa).get(votante = coordinadorLinea)
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
							### envio el email al coordinador y al profeEncargado
						# message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
		    #         	message.to = coordinadorLinea.email
		    #             message.html """"
						# 			<html><head></head><body>
						# 			Estimado:

						# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
						# 			Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , ha sido exitosa
						# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
						# 			Saludos
						# 			</body></html>
						# 		"""%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

		    #             message.send()
		    #             message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
		    #         	message.to = profe.email
		    #             message.html """"
						# 			<html><head></head><body>
						# 			Estimado:

						# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
						# 			Asociadas a lo definido en el programa de asignatura %s %s %s, ha sido exitosa
						# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
						# 			Saludos
						# 			</body></html>
						# 		"""%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

		    #             message.send()

							programa.save()
						else:
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

							#message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
			      #       	message.to = coordinadorLinea.email
			      #           message.html """"
									# 	<html><head></head><body>
									# 	Estimado:

									# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
									# 	Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , no ha sido exitosa
									# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
									# 	Saludos
									# 	</body></html>
									# """%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

			      #           message.send()
			      #           message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
			      #       	message.to = profe.email
			      #           message.html """"
									# 	<html><head></head><body>
									# 	Estimado:

									# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
									# 	Asociadas a lo definido en el programa de asignatura %s %s %s, no ha sido exitosa
									# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
									# 	Saludos.




									# 	</body></html>
									# """%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

			      #           message.send()
								
							## PErdieorn
				else:
					termino = 0



	ctx = {'form': form, 'p' : programa, 'username': request.user.username, 'votos': votos, 'estado': voteYo, 'termino':termino, 'perdieron': perdieron}

	return render(request, 'formulacion/evaluacionAsociadaOther.html', ctx)

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
	 		programa.fechaUltimaModificacion = datetime.now()
	 		logEstado(programa, programa.state.title)
	 		definicion.estado = "Finalizado"
	 		definicion.save()
	 		programa.save()
	 		return HttpResponseRedirect('/intermedioAdmRec/'+id_programa)
		else:
	           ## guardamos el producto 
			definicion.estado = "Modificando"
	 		definicion.save()
			programa.fechaUltimaModificacion = datetime.now()
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
	 		programa.fechaUltimaModificacion = datetime.now()
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
			programa.fechaUltimaModificacion = datetime.now()
			programa.save()	
			return HttpResponseRedirect('/intermedioAdmRec/')
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
	 		programa.fechaUltimaModificacion = datetime.now()
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
			programa.fechaUltimaModificacion = datetime.now()
			programa.save()	
			return HttpResponseRedirect('/intermedioAdmRec/')
	ctx = {'form': form, 'p' : programa, 'form': form, 'username': request.user.username}
	return render(request, 'formulacion/recursosAprendizaje.html', ctx)

def preAnalisisView(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	programa.to_aprobPrograma()
	logEstado(programa, programa.state.title)
	programa.fechaUltimaModificacion = datetime.now()
	programa.save()
	form = analisisLineaForm()
	profe = programa.profesorEncargado
	linea = Profesor.objects.get(user = profe).linea
	coordinadorLinea = linea.coordinador
	profesoresLinea = Profesor.objects.filter(linea=linea).count()
	votos = Analisis.objects.filter(programa=programa)
	perdieron = 0
	termino = 0
	estadoMiVoto = 'no'
	try:
		voteYo = Analisis.objects.filter(programa=programa).get(votante=profe)
	except:
		voteYo = None
	if voteYo is not None:
		voteYo = 1
	else:
		voteYo = 0
	## ver si voto el coordinador ##
	try:
		votoCoord = Analisis.objects.get(votante=coordinadorLinea)
	except:
		votoCoord = 0
	if votoCoord is None:
		votoCoord = 1
	else:
		votoCoord = 0

	if len(votos) != 0 :
		numVotos = Analisis.objects.filter(programa=programa).count()
		
		if numVotos == (profesoresLinea + 1):
			## todos votaron
			termino = 1
			votosSi = votos.filter(voto='Si').count()
			votosNo =  votos.filter(voto='No').count()
			if votosSi>votosNo :

				## si hay evaluaciones
				## se envia email al profe y al coordinador
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
				### envio el email al coordinador y al profeEncargado
				# message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
    #         	message.to = coordinadorLinea.email
    #             message.html """"
				# 			<html><head></head><body>
				# 			Estimado:

				# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
				# 			Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , ha sido exitosa
				# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
				# 			Saludos
				# 			</body></html>
				# 		"""%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

    #             message.send()
    #             message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
    #         	message.to = profe.email
    #             message.html """"
				# 			<html><head></head><body>
				# 			Estimado:

				# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
				# 			Asociadas a lo definido en el programa de asignatura %s %s %s, ha sido exitosa
				# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
				# 			Saludos
				# 			</body></html>
				# 		"""%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

    #             message.send()
				programa.save()

			if votosSi<votosNo:
				perdieron = 1
				programa.noAprob_toForm()
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

				#message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
      #       	message.to = coordinadorLinea.email
      #           message.html """"
						# 	<html><head></head><body>
						# 	Estimado:

						# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
						# 	Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , no ha sido exitosa
						# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
						# 	Saludos
						# 	</body></html>
						# """%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

      #           message.send()
      #           message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
      #       	message.to = profe.email
      #           message.html """"
						# 	<html><head></head><body>
						# 	Estimado:

						# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
						# 	Asociadas a lo definido en el programa de asignatura %s %s %s, no ha sido exitosa
						# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
						# 	Saludos.




						# 	</body></html>
						# """%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

      #           message.send()
			if votosNo==votosSi:
				## veo el voto del coordinador
				votoDelCoord = Analisis.objects.filter(programa = id_programa).get(votante = coordinadorLinea)
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
					### envio el email al coordinador y al profeEncargado
				# message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
    #         	message.to = coordinadorLinea.email
    #             message.html """"
				# 			<html><head></head><body>
				# 			Estimado:

				# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
				# 			Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , ha sido exitosa
				# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
				# 			Saludos
				# 			</body></html>
				# 		"""%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

    #             message.send()
    #             message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
    #         	message.to = profe.email
    #             message.html """"
				# 			<html><head></head><body>
				# 			Estimado:

				# 			Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
				# 			Asociadas a lo definido en el programa de asignatura %s %s %s, ha sido exitosa
				# 			por lo que el programa ha pasado al estado de Verificacion de Completitud y Coherencia.
				# 			Saludos
				# 			</body></html>
				# 		"""%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

    #             message.send()

					programa.save()
				else:
					perdieron = 1
					programa.noAprob_toForm()
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

					#message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
	      #       	message.to = coordinadorLinea.email
	      #           message.html """"
							# 	<html><head></head><body>
							# 	Estimado:

							# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
							# 	Asociadas a lo definido en el programa de asignatura %s %s %s del profesor %s %s , no ha sido exitosa
							# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
							# 	Saludos
							# 	</body></html>
							# """%(programa.asignatura, programa.semestre, programa.ano, profe.first_name, profe.last_name)

	      #           message.send()
	      #           message = Email.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",subject="Votacion Evaluaciones Asociadas")
	      #       	message.to = profe.email
	      #           message.html """"
							# 	<html><head></head><body>
							# 	Estimado:

							# 	Le informamos que el resultado de la votacion realizado sobre la existencia de Evaluaciones 
							# 	Asociadas a lo definido en el programa de asignatura %s %s %s, no ha sido exitosa
							# 	por lo que el programa ha vuelto al estado de Formulacion de Programa, para su analisis.
							# 	Saludos.




							# 	</body></html>
							# """%(programa.asignatura, programa.semestre, programa.ano, profesor.first_name, profesor.last_name)

	      #           message.send()
						
		else:
			termino = 0
	if request.method == 'POST':
		form = analisisLineaForm(request.POST)
		if form.is_valid():
			voto = form.cleaned_data['voto']
			observacion = form.cleaned_data['observacion']
			votante = request.user
			evaluacion = Analisis.objects.create(voto = voto, observacion=observacion, votante=votante, programa=programa)
			evaluacion.save()
			return HttpResponseRedirect('/preAnalisis/'+id_programa)
	ctx = {'form': form, 'p' : programa, 'username': request.user.username, 'votos': votos, 'estado': voteYo, 'termino':termino, 'perdieron': perdieron}
	return render(request, 'formulacion/analisisProgramaOwn.html', ctx)


def fastTrackView(request, id_programa, decision):
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
			logEstado(p, p.state.title)
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
        else:
            m.cantidad = m.cantidad - 1
            m.save()
            programa.noFT_toAnalisisJC()
            logEstado(p, p.state.title)
            programa.save()
            try:
                n = ProgramasPorEstado.objects.get(estado=programa.state.title)
            except ProgramasPorEstado.DoesNotExist:
                n = None
            if n is None:
                newIndicador2 = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
                newIndicador2.save()
            else:
                n.cantidad = y.cantidad + 1
                n.save()
            return HttpResponseRedirect('/programasPorAnalizarLinea/')



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
	 	
	# if (estado == 'aprobacionLinea' ):
	# 	return HttpResponseRedirect('/aprobacionLinea/'+id_programa)
	# if (estado == 'fastTrack' ):
	# 	return HttpResponseRedirect('/fastTrack/'+id_programa)
	# if (estado == 'definicionClaseClase' ):
	# 	return HttpResponseRedirect('/definicionClaseClase/'+id_programa)
	# if (estado == 'analisisProgramaJC' ):
	# 	return HttpResponseRedirect('/analisisProgramaJC/'+id_programa)
	# if (estado == 'indicacionModificacion'):
	# 	return HttpResponseRedirect('/indicacionModificacion/'+id_programa)
	# if (estado == 'aprobacionProgramaJC'):
	# 	return HttpResponseRedirect('/aprobacionProgramaJC/'+id_programa)

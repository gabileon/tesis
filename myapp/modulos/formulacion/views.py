from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from datetime import datetime
from myapp.modulos.formulacion.models import Programa, MyWorkflow, Recurso, Objetivo, Capacidad, Contenido, ClaseClase, Completitud
from myapp.modulos.formulacion.forms import estadoForm, decisionEvaluacionForm, crearProgramaForm, definirObjetivosForm, definirCompletitudForm, definirCapacidadesForm, definirContenidosForm, definirClaseClaseForm
from myapp.modulos.presentacion.models import CredentialsModel
from myapp import settings
from myapp.modulos.indicadores.models import ProgramasPorEstado
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build
import httplib2
import os


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
  			return HttpResponseRedirect('/definiciones/'+id_programa)
 		else:
 			return HttpResponseRedirect('/principalPL/')
 	ctx = {'url': url, 'p': programa, 'form':form, 'recursos': recursos}
 	return render(request, 'formulacion/definicionesGenerales.html', ctx)


def definicionesGeneralesAdmin(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	username=request.user.username
	ctx = {'p': programa, 'username': username}
	return render(request, 'formulacion/definiciones.html', ctx)

def definicionConstribucion(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	form = estadoForm()
	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_defGeneralCons()
	 		programa.objetivo.estadoObj = "Finalizado"
	 		programa.objetivo.save()
	 		programa.save()
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
	 		return HttpResponseRedirect('/definiciones/'+id_programa)
		#programa.to_defObj()
		else:
	           ## guardamos el producto 
			programa.objetivo.estadoObj = "Modificando"
			programa.objetivo.save()
			programa.to_defGeneralCons()
			programa.save()
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
	    	return HttpResponseRedirect('/definiciones/'+id_programa)
	programa.to_defCons()
	programa.save()
	ctx = {'form': form, 'p' : programa, 'form': form}
	return render(request, 'formulacion/definicionConstribucion.html', ctx)

def definicionRdA(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	form = estadoForm()
	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_defGeneralRdA()
	 		programa.capacidad.estadoCapac = "Finalizado"
	 		programa.capacidad.save()
	 		programa.save()
	 		return HttpResponseRedirect('/definiciones/'+id_programa)
		#programa.to_defObj()
		else:
	           ## guardamos el producto 
			programa.capacidad.estadoCapac = "Modificando"
			programa.capacidad.save()
			programa.to_defGeneralRdA()
			programa.save()
	    	return HttpResponseRedirect('/definiciones/'+id_programa)
	programa.to_defRdA()
	programa.save()
	ctx = {'form': form, 'p' : programa, 'form': form}
	return render(request, 'formulacion/definicionRdA.html', ctx)

def definicionEstra(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	form = estadoForm()
	
	if request.method == "POST":
		form = estadoForm(request.POST)
		choice = request.POST['optionsRadios']
		if choice=='option2':
	 		programa.to_defGeneralEstra()
	 		programa.contenido.estadoCont = "Finalizado"
	 		programa.contenido.save()
	 		programa.save()
	 		return HttpResponseRedirect('/definiciones/'+id_programa)
		#programa.to_defObj()
		else:
	           ## guardamos el producto 
			programa.contenido.estadoCont = "Modificando"
			programa.contenido.save()
			programa.to_defGeneralEstra()
			programa.save()
	    	return HttpResponseRedirect('/definiciones/'+id_programa)
	programa.to_defEstrategias()
	programa.save()
	ctx = {'form': form, 'p' : programa, 'form': form}
	return render(request, 'formulacion/definicionEstra.html', ctx)


# def definicionContenidos_view(request, id_programa):
# 	programa = Programa.objects.get(id=id_programa)	
# 	if request.method == "POST":
		
# 		form = definirContenidosForm(request.POST)
# 		#programa.to_defObj()
# 		if form.is_valid():
# 			##si es valido, inicializo las variables
# 			contenidos = form.cleaned_data['contenidos']		
# 			### se crea programa
# 			programa.contenido.contenidosPrograma= contenidos
# 	           ## guardamos el producto 
# 	    	programa.contenido.estadoCont = "Finalizado"
# 	    	programa.contenido.save()
# 	    	programa.to_defGeneralCont()
	    	
# 		form = definirContenidosForm()
# 		#id_programa = 
# 		ctx = {'form': form, 'p' : programa}
# 		return render(request, 'formulacion/definiciones.html', ctx)
# 	else:
# 		#GEt
# 		programa.to_defCont()
# 		form = definirContenidosForm()
# 		ctx = {'form': form, 'p':programa}
# 		return render(request, 'formulacion/definicionContenidos.html', ctx)

# def definicionClaseClase_view(request, id_programa):
# 	programa = Programa.objects.get(id=id_programa)	
# 	#programa.to_defObj()
# 	if request.method == "POST":
# 		form = definirClaseClaseForm(request.POST)
# 		#programa.to_defObj()
# 		if form.is_valid():
# 				##si es valido, inicializo las variables
# 			claseclase = form.cleaned_data['claseclase']		
# 			### se crea programa
# 			programa.claseclase.claseclase = claseclase
# 	           ## guardamos el producto 
# 	        programa.to_analisisEval()
# 	    	programa.claseclase.save()
# 		form = definirClaseClaseForm()
# 		#id_programa = 
# 		ctx = {'form': form, 'p' : programa}
# 		return render(request, 'formulacion/vistaResumen.html', ctx)
# 	else:
# 		#GEt
# 		programa.to_defObj()
# 		programa.to_defClase()
# 		form = definirClaseClaseForm()
# 		ctx = {'form': form, 'p':programa}
# 		return render(request, 'formulacion/definicionClaseClase.html', ctx)

# def definicionClaseClaseR_view(request, id_programa):
# 	programa = Programa.objects.get(id=id_programa)
# 	ctx = {'p': programa}
# 	if request.method == "POST":
# 		if 'Existen' in request.POST:
# 			programa.siEvaluacion_toVerif()
# 			programa.save()
# 			return render(request,'formulacion/completitud.html', ctx)
# 		if 'noExisten' in request.POST:
# 			programa.noEvaluacion_toForm()
# 			programa.to_defGeneral()
# 			programa.save()
# 			return render(request, 'formulacion/definiciones.html', ctx)

# def definicionCompletitudCoherencia_view(request, id_programa):
# 	programa = Programa.objects.get(id=id_programa)
# 	#programa.to_defObj()
# 	if request.method == "POST":
# 		form = definirCompletitudForm(request.POST)
# 		#programa.to_defObj()
# 		if form.is_valid():
# 			##si es valido, inicializo las variables
# 			completitud= form.cleaned_data['completitud']		
# 			### se crea programa
# 			programa.completitud.completitudPrograma = completitud
# 	    	programa.completitud.save()
# 	    	programa.to_aprobPrograma()
# 		form = definirCompletitudForm()
# 		ctx = {'form': form, 'p' : programa}
# 		return render(request, 'formulacion/vistaResumen2.html', ctx)
# 	else:
# 		#GEt
# 		programa.to_defCap()
# 		form = definirCompletitudForm()
# 		ctx = {'form': form, 'p':programa}
# 		return render(request, 'formulacion/completitud.html', ctx)

# def resumen2_view(request, id_programa): 
# 	#aprueba linea de profesores
# 	programa = Programa.objects.get(id=id_programa)
# 	ctx = {'p': programa}
# 	if request.method == "POST":
# 		if 'Aprueba' in request.POST:
# 			programa.siAprob_toFT()
# 			programa.save()
# 			return render(request, 'formulacion/fastrack.html', ctx)
# 		if 'noAprueba' in request.POST:
# 			programa.noAprob_toForm()
# 			programa.to_defGeneral()
# 			programa.save()
# 			return render(request, 'formulacion/definiciones.html', ctx)

# def fasttrack_view(request, id_programa):
# 	programa = Programa.objects.get(id=id_programa)
# 	ctx = {'p': programa}
# 	if request.method == "POST":
# 		if 'Si' in request.POST:
# 			programa.siFT_toAprobJC()
# 			programa.save()
# 			return render(request, 'formulacion/vistaJefeCarrera.html', ctx)
# 		if 'No' in request.POST:
# 			programa.noFT_toAnalisisJC()
# 			programa.save()
# 			return render(request, 'formulacion/analisisPrograma.html', ctx)

# def analisisPrograma_view(request, id_programa):
# 	programa = Programa.objects.get(id=id_programa)
# 	ctx = {'p': programa}
# 	programa.to_indicModif()
# 	if request.method == "POST":
# 		if 'noIndic' in request.POST:
# 			programa.noIndic_toAprobJC()
# 			programa.save()
# 			return render(request, 'formulacion/vistaJefeCarrera.html', ctx)
# 		if 'Indic' in request.POST:
# 			programa.siIndic_toForm()
# 			programa.to_defGeneral()
# 			programa.save()
# 			return render(request, 'formulacion/definiciones.html', ctx)

# def aprobacionPrograma_view(request, id_programa):
# 	programa = Programa.objects.get(id=id_programa)
# 	ctx = {'p': programa}
# 	if request.method == "POST":
# 		if 'Aprueba' in request.POST:
# 			programa.siAprob_toFin()
# 			programa.save()
# 			return HttpResponse("Programa: " + programa.asignatura + " aprobado.  Estado:  " + programa.state.title)
# 		if 'noAprueba' in request.POST:
# 			programa.noAprobJC_toForm()
# 			programa.to_defGeneral()
# 			programa.save()
# 			return render(request, 'formulacion/definiciones.html', ctx)

def buscarEstado(request, id_programa, estado):
	if (estado == 'definicionDatosAsignatura' ):
		return HttpResponseRedirect('/definicionesGenerales/'+id_programa)
	if (estado == 'definicionGeneral'):
		return HttpResponseRedirect('/definiciones/'+id_programa)
	if (estado == 'definicionConstribucion' ):
	 	return HttpResponseRedirect('/definicionConstribucion/'+id_programa )
	if (estado == 'definicionRdA' ):
	 	return HttpResponseRedirect('/definicionRdA/'+id_programa)
	# if (estado == 'definicionEstrategias' ):
	# 	return HttpResponseRedirect('/definicionEstrategias/'+id_programa)
	# if (estado == 'definicionClaseClase' ):
	# 	return HttpResponseRedirect('/definicionClaseClase/'+id_programa)
	# if (estado == 'analisisEvaluacionesAsociadas' ):
	# 	return HttpResponseRedirect('/analisisEvaluacionesAsociadas/'+id_programa)
	# if (estado == 'verificacionCoherenciaCompletitud'):
	# 	return HttpResponseRedirect('/verificacionCoherenciaCompletitud/'+id_programa)
	# if (estado == 'programacionActividades'):
	# 	return HttpResponseRedirect('/programacionActividades/'+id_programa)
	# if (estado == 'definicionAspecAdmin' ):
	# 	return HttpResponseRedirect('/definicionAspecAdmin/'+id_programa)
	# if (estado ==  'definicionRecursos' ):
	# 	return HttpResponseRedirect('/definicionRecursos/'+id_programa)
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

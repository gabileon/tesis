from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from myapp.modulos.formulacion.models import Programa, MyWorkflow, Objetivo, Capacidad, Contenido, ClaseClase, Completitud
from myapp.modulos.formulacion.forms import decisionEvaluacionForm, crearProgramaForm, definirObjetivosForm, definirCompletitudForm, definirCapacidadesForm, definirContenidosForm, definirClaseClaseForm

def crearPrograma(request):
	if request.method == "POST":
		p = Programa()
		#p.to_formulacion()
		form = crearProgramaForm(request.POST)
		if form.is_valid():
				##si es valido, inicializo las variables
			asignatura = form.cleaned_data['asignatura']
			semestre = form.cleaned_data['semestre']
			ano = form.cleaned_data['ano']
			### se crea programa
			p.asignatura = asignatura
			p.semestre = semestre
			p.ano = ano	
			p.to_formulacion()
	    	p.to_defGeneral()  	
	    	  ## guardamos el programa
	    	p.save()
	    	objetivo = Objetivo(programa=p)
	    	capacidad = Capacidad(programa=p)
	    	contenido = Contenido(programa=p)
	    	clase = ClaseClase(programa=p)
	    	completitud = Completitud(programa=p)
	    	objetivo.save()
	    	capacidad.save()
	    	contenido.save()
	    	clase.save()
	    	completitud.save()
	    	## cambio el estado ##    	
		form = crearProgramaForm()
		ctx = {'form': form, 'p' : p}
		return render(request, 'formulacion/definiciones.html', ctx)
	else:
		#GEt
		form = crearProgramaForm()
		ctx = {'form': form}
		return render(request, 'formulacion/definicionesGenerales.html', ctx)
	#log(p.id)

def definiciones(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	if request.method == "POST":
		if 'Existen' in request.POST:
			programa.siEvaluacion_toVerif()
			programa.save()
			return render(request, '/formulacion/completitud.html', ctx)
		
	ctx = {'p': programa}
	#return HttpResponse(contenido.estadoCont)
	return render(request, 'formulacion/definiciones.html', ctx)

def definicionObjetivos(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	#programa.to_defObj()
	if request.method == "POST":
		
		form = definirObjetivosForm(request.POST)
		#programa.to_defObj()
		if form.is_valid():
				##si es valido, inicializo las variables
			objetivos = form.cleaned_data['objetivos']		
			### se crea programa
			programa.objetivo.objetivosPrograma = objetivos
	           ## guardamos el producto 
	    	programa.objetivo.estadoObj = "Finalizado"
	    	programa.objetivo.save()
	    	programa.to_defGeneralObj()
		form = definirObjetivosForm() 
		ctx = {'form': form, 'p' : programa}
		return render(request, 'formulacion/definiciones.html', ctx)
	else:
		#GEt
		programa.to_defObj()
		form = definirObjetivosForm()
		ctx = {'form': form, 'p':programa}
		return render(request, 'formulacion/definicionObjetivos.html', ctx)

def definicionCapacidades_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	#programa.to_defObj()
	if request.method == "POST":
		
		form = definirCapacidadesForm(request.POST)
		#programa.to_defObj()
		if form.is_valid():
				##si es valido, inicializo las variables
			capacidades = form.cleaned_data['capacidades']		
			### se crea programa
			programa.capacidad.capacidadesPrograma = capacidades
	           ## guardamos el producto 
	    	programa.capacidad.estadoCapac = "Finalizado"
	    	programa.capacidad.save()
	    	programa.to_defGeneralCap()
		form = definirCapacidadesForm() 
		ctx = {'form': form, 'p' : programa}
		return render(request, 'formulacion/definiciones.html', ctx)
	else:
		#GEt
		programa.to_defCap()
		form = definirCapacidadesForm() 
		ctx = {'form': form, 'p':programa}
		return render(request, 'formulacion/definicionCapacidades.html', ctx)

def definicionContenidos_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)	
	if request.method == "POST":
		
		form = definirContenidosForm(request.POST)
		#programa.to_defObj()
		if form.is_valid():
			##si es valido, inicializo las variables
			contenidos = form.cleaned_data['contenidos']		
			### se crea programa
			programa.contenido.contenidosPrograma= contenidos
	           ## guardamos el producto 
	    	programa.contenido.estadoCont = "Finalizado"
	    	programa.contenido.save()
	    	programa.to_defGeneralCont()
	    	
		form = definirContenidosForm()
		#id_programa = 
		ctx = {'form': form, 'p' : programa}
		return render(request, 'formulacion/definiciones.html', ctx)
	else:
		#GEt
		programa.to_defCont()
		form = definirContenidosForm()
		ctx = {'form': form, 'p':programa}
		return render(request, 'formulacion/definicionContenidos.html', ctx)

def definicionClaseClase_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)	
	#programa.to_defObj()
	if request.method == "POST":
		form = definirClaseClaseForm(request.POST)
		#programa.to_defObj()
		if form.is_valid():
				##si es valido, inicializo las variables
			claseclase = form.cleaned_data['claseclase']		
			### se crea programa
			programa.claseclase.claseclase = claseclase
	           ## guardamos el producto 
	        programa.to_analisisEval()
	    	programa.claseclase.save()
		form = definirClaseClaseForm()
		#id_programa = 
		ctx = {'form': form, 'p' : programa}
		return render(request, 'formulacion/vistaResumen.html', ctx)
	else:
		#GEt
		programa.to_defObj()
		programa.to_defClase()
		form = definirClaseClaseForm()
		ctx = {'form': form, 'p':programa}
		return render(request, 'formulacion/definicionClaseClase.html', ctx)

def definicionClaseClaseR_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	ctx = {'p': programa}
	if request.method == "POST":
		if 'Existen' in request.POST:
			programa.siEvaluacion_toVerif()
			programa.save()
			return render(request,'formulacion/completitud.html', ctx)
			# return HttpResponse("HOLAAAAAAAAAAA")
		if 'noExisten' in request.POST:
			programa.noEvaluacion_toForm()
			programa.to_defGeneral()
			programa.save()
			return render(request, 'formulacion/definiciones.html', ctx)

def definicionCompletitudCoherencia_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	#programa.to_defObj()
	if request.method == "POST":
		form = definirCompletitudForm(request.POST)
		#programa.to_defObj()
		if form.is_valid():
			##si es valido, inicializo las variables
			completitud= form.cleaned_data['completitud']		
			### se crea programa
			programa.completitud.completitudPrograma = completitud
	    	programa.completitud.save()
	    	programa.to_aprobPrograma()
		form = definirCompletitudForm()
		ctx = {'form': form, 'p' : programa}
		return render(request, 'formulacion/vistaResumen2.html', ctx)
	else:
		#GEt
		programa.to_defCap()
		form = definirCompletitudForm()
		ctx = {'form': form, 'p':programa}
		return render(request, 'formulacion/completitud.html', ctx)

def resumen2_view(request, id_programa): 
	#aprueba linea de profesores
	programa = Programa.objects.get(id=id_programa)
	ctx = {'p': programa}
	if request.method == "POST":
		if 'Aprueba' in request.POST:
			programa.siAprob_toFT()
			programa.save()
			return render(request, 'formulacion/fastrack.html', ctx)
			# return HttpResponse("HOLAAAAAAAAAAA")
		if 'noAprueba' in request.POST:
			programa.noAprob_toForm()
			programa.to_defGeneral()
			programa.save()
			return render(request, 'formulacion/definiciones.html', ctx)

def fasttrack_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	ctx = {'p': programa}
	if request.method == "POST":
		if 'Si' in request.POST:
			programa.siFT_toAprobJC()
			programa.save()
			return render(request, 'formulacion/vistaJefeCarrera.html', ctx)
		if 'No' in request.POST:
			programa.noFT_toAnalisisJC()
			programa.save()
			return render(request, 'formulacion/analisisPrograma.html', ctx)

def analisisPrograma_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	ctx = {'p': programa}
	programa.to_indicModif()
	if request.method == "POST":
		if 'noIndic' in request.POST:
			programa.noIndic_toAprobJC()
			programa.save()
			return render(request, 'formulacion/vistaJefeCarrera.html', ctx)
		if 'Indic' in request.POST:
			programa.siIndic_toForm()
			programa.to_defGeneral()
			programa.save()
			return render(request, 'formulacion/definiciones.html', ctx)

def aprobacionPrograma_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	ctx = {'p': programa}
	if request.method == "POST":
		if 'Aprueba' in request.POST:
			programa.siAprob_toFin()
			programa.save()
			return HttpResponse("Programa: " + programa.asignatura + " aprobado.  Estado:  " + programa.state.title)
		if 'noAprueba' in request.POST:
			programa.noAprobJC_toForm()
			programa.to_defGeneral()
			programa.save()
			return render(request, 'formulacion/definiciones.html', ctx)

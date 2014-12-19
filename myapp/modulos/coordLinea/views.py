from django.shortcuts import render, redirect
import datetime, random, sha
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from myapp.modulos.presentacion.models import UserProfile
from myapp.modulos.presentacion.forms import cambiarDatosForm
from myapp.modulos.formulacion.models import Log, Evaluacion, Evaluaciones, Analisis, Log, Profesor, Programa, MyWorkflow,  ClaseClase, Linea, Asignatura, Recurso
from myapp.modulos.presentacion.forms import ImageUploadForm
from myapp.modulos.jefeCarrera.models import Evento, ReporteIndic
from myapp.modulos.coordLinea.forms import CoordinadorForm
from myapp.modulos.formulacion.forms import LineasForm, UploadFileForm, analizarForm, evaluacionesForm, analisisLineaForm
from myapp.modulos.jefeCarrera.forms import changePasswordForm, AgregarEventoCordForm, AgregarEventoForm,  agregarAsignaturaForm, agregarProfesoresForm
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from myapp.modulos.presentacion.models import CredentialsModel
from apiclient.discovery import build
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from apiclient.discovery import build
import httplib2
import os
from myapp import settings
import httplib2
from myapp.modulos.jefeCarrera.hora import build_rfc3339_phrase
from google.appengine.api import mail
from myapp.modulos.indicadores.models import ProgramasPorEstado
from apiclient.discovery import build
from apiclient.http import MediaFileUpload

FILENAME = 'hola.txt'


def fastTrackView(request):
    programas = Programa.objects.filter(state='fastTrack')
    username = request.user.username
    ctx = {'username': username, 'programas': programas}
    return render (request, 'coordLinea/progPorAnalizarFT.html', ctx)



# Create your views here.
def logEstado (programa, state):
    l= Log()
    l.programa = programa
    l.state = state
    l.fecha = datetime.now() - timedelta(hours=3)
    l.save()    

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive' ' https://www.googleapis.com/auth/calendar ',
    redirect_uri=settings.REDIRECT_URI)

def reportesIndicacionCordView(request):
    reportes = ReporteIndic.objects.all()
    return render(request, 'coordLinea/reportesIndicaciones.html', {'reportes':reportes, 'username': request.user.username})

def RolView(request, id_user):
    user = User.objects.get(id=id_user)
    perfil = UserProfile.objects.get(user=user.id)
    return render(request, 'presentacion/cambiarRol.html', {'user':user, 'perfil':perfil})

def cambiarRolView(request, id_user, rol):
    user = User.objects.get(id=id_user)
    perfil = UserProfile.objects.get(user=user.id)
    if rol == 'PL':
        perfil.rol_actual = 'PL'
        perfil.save()
        if perfil.fechaPrimerAcceso is None:
            return redirect('/cambiarDatosProfe/')
        else:
            return HttpResponseRedirect('/principal_cl/')
        return HttpResponseRedirect('/principalPL/')
    if rol == 'JC':
        perfil.rol_actual = 'JC'
        perfil.save()
        return HttpResponseRedirect('/principal_jc/')
    if rol == 'CL':
        perfil.rol_actual = 'CL'
        perfil.save()
        if perfil.fechaPrimerAcceso is None:
            return redirect('/cambiarDatosCord/')
        else:
            return HttpResponseRedirect('/principal_cl/')

def revisarRol (request):
    user = User.objects.get(username=request.user.username)
    perfil = UserProfile.objects.get(user=user.id)
    bandera = None
    if perfil.rol_actual == 'CL':
        pass
    else:
        return redirect ('/errorLogin/')

def principalCLView(request):
    user = User.objects.get(username=request.user.username)
    perfil = UserProfile.objects.get(user=user.id)
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        programa = Programa.objects.all().order_by('-fechaUltimaModificacion')
        programasAprobados= Programa.objects.filter(state='fin').count()
        programasPorAnalizar = Programa.objects.filter(state='aprobacionLinea')
        fast = Programa.objects.filter(state='fastTrack').count()
        todos = Programa.objects.filter(state='analisisEvaluacionesAsociadas')
        analisis = []
        votaciones = []
        for p in programasPorAnalizar:
            if p.analisism.votoEvalCord==False:
                analisis.append(p)
        numAnalisis = len(analisis)
        for p in todos:
            if p.analisism.votoEvalCord==False:
                votaciones.append(p)
        numEval = len(votaciones)
        username = request.user.username
        userTemp = User.objects.get(username=request.user.username)
        profile = UserProfile.objects.get(user=userTemp)
        linea = Linea.objects.get(id=profile.cordLinea_id)
        ctx = {'user': userTemp, 'username' : username, 'programas':programa, 'fast': fast, 'votaciones': numEval, 'porAnalizar': numAnalisis, 'aprobados' : programasAprobados, 'profile': profile, 'linea':linea}
        return render(request, 'coordLinea/vistaCL.html', ctx)
    else:
        return redirect ('/errorLogin/')

def votacionesEvaluacionView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        evaluaciones = Evaluacion.objects.filter(votoEvalCord=False)
        form = evaluacionesForm()
        ctx = {'username': request.user.username, 'programas': evaluaciones, 'form': form}
        return render (request, 'coordLinea/votaciones.html', ctx)
    else:
        return redirect ('/errorLogin/')
############ votacion evaluaciones asociadas ########
def votacion (request, id_evaluacion):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        evaluacion = Evaluacion.objects.get(id=id_evaluacion)
        if request.method == 'POST':
            form = evaluacionesForm(request.POST)
            if form.is_valid():
                voto = form.cleaned_data['voto']
                observacion = form.cleaned_data['observacion']
                votante = request.user
                evaluac = Evaluaciones.objects.create(voto = voto, observacion=observacion, votante=votante, evaluacion= evaluacion)
                evaluac.save()
                evaluacion.votoEvalCord = True
                evaluacion.save()
                evaluacionesVot(evaluacion)
                return HttpResponseRedirect('/votacionesEvaluacionLinea/')
    else:
        return redirect ('/errorLogin/')

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

def changePasswordCordView(request, id_user):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        u = User.objects.get(id=id_user)
        form = changePasswordForm()
        if request.method == "POST":
            form = changePasswordForm(request.POST)
            if form.is_valid():
                old_password = form.cleaned_data['old_password']
                password = form.cleaned_data['password']
                if u is not None and u.check_password(old_password):
                    u.set_password(password)
                    u.save()
                    return HttpResponseRedirect("/miperfil/")
        ctx = {'form':form, 'user':u, 'username': request.user.username}
        return render(request, 'presentacion/changePasswordCord.html', ctx)
    else:
        return redirect ('/errorLogin/')

def cambiarDatosCordView(request ):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
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
                redirect ('/miperfilCord/')
        ctx = {'form': form, 'username': request.user.username}
        return render(request, 'coordLinea/cambiarDatos.html', ctx)
    else:
        return redirect ('/errorLogin/')

def miperfilCordView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        userTemp = User.objects.get(username=request.user.username)
        perfilTemp = UserProfile.objects.get(user=userTemp.id)
        
        try:
            linea = Linea.objects.get(coordinador=userTemp.id)
        except Linea.DoesNotExist:
            linea = None
        ctx = {'user': userTemp, 'perfil': perfilTemp, 'linea':linea, 'username': request.user.username}
        if request.method == 'POST':
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                foto = form.cleaned_data['image']
                perfilTemp.foto = foto 
                perfilTemp.save()
                return redirect('/miperfil/')
        return render(request, 'coordLinea/perfilConf.html', ctx)
    else:
        return redirect ('/errorLogin/')

def crearFechasCoord(request):
    hoy = datetime.now()
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        userTemp = User.objects.get(username=request.user.username)
        profile = UserProfile.objects.get(user=userTemp)
        linea = Linea.objects.get(id=profile.cordLinea_id)
        eventos = Evento.objects.filter(anfitrion=request.user).filter(start__range=(hoy - timedelta(days=1), hoy + timedelta(days=200)))
        todos = Evento.objects.all().filter(start__range=(hoy - timedelta(days=1), hoy + timedelta(days=200)))
        try:
            storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
            credential = storage.get()
            http= httplib2.Http()
            http= credential.authorize(http)
            service = build('calendar', 'v3', http=http)
        except:
            return redirect('/logout/')

        calendar_list_entry = service.calendarList().get(calendarId='primary').execute()
        form = AgregarEventoCordForm()
        if request.method == 'POST':
            form = AgregarEventoCordForm(request.POST)
            if form.is_valid():
                summary = form.cleaned_data['summary']
                location = form.cleaned_data['location']
                descripcion = form.cleaned_data['descripcion']
                tipoEvento = form.cleaned_data['tipoEvento']
                start = form.cleaned_data['start']
                inicio = build_rfc3339_phrase(start)
                end = form.cleaned_data['end']
                fin = build_rfc3339_phrase(end)
                nuevoEvent = Evento()
                temp = Evento()
                if tipoEvento == 'profesor' :
                    profesores = Profesor.objects.filter(linea=linea.id)
                    event = {
                        'summary': '%s'%(summary),
     
                        'start': {
                            'dateTime': '%s'%(inicio),
                            # 'timeZone': 'America/Santiago'
                          },
                        'end': {
                            'dateTime': '%s'%(fin),
                            # 'timeZone': 'America/Santiago'
                          }
                                        }               
                    invitados = []
                    emails  = []
                    for email in profesores:
                        x = {}
                        x.update({'email': email.user.email})
                        invitados.append(email.user.email)
                        emails.append(x)

                    event.update({'attendees': emails})
                    created_event = service.events().insert(calendarId='primary', body=event).execute()
                    nuevoEvento = Evento.objects.create(summary= summary, location = location, start =start, end=end, 
                    descripcion=descripcion, id_calendar=created_event['id'], tipoEvento=tipoEvento, anfitrion=request.user, invitados =invitados)
                    nuevoEvento.save()

                if tipoEvento == 'jefe':
                    jefeCarrera = UserProfile.objects.get(rol_JC='JC')
                    linea = Linea.objects.get(nombreLinea = 'Proyectos')
                    # coordinador = linea.coordinador.email
                    event = {
                        'summary': '%s'%(summary),
     
                        'start': {
                            'dateTime': '%s'%(inicio),
                            # 'timeZone': 'America/Santiago'
                          },
                        'end': {
                            'dateTime': '%s'%(fin),
                            # 'timeZone': 'America/Santiago'
                          }}
                    event['attendees'] =  [{'email': jefeCarrera.user.email}]
                    created_event = service.events().insert(calendarId='primary', body=event).execute()     
                    nuevoEvento = Evento.objects.create(summary= summary, location = location, start =start, end=end, 
                    descripcion=descripcion,  id_calendar=created_event['id'], tipoEvento=tipoEvento , anfitrion=request.user, invitados =jefeCarrera.user.email)
                      
                    nuevoEvento.save()
        else:
            form = AgregarEventoCordForm()
        ctx = {'form':form, 'eventos': eventos, 'username': request.user.username, 'todos': todos}    
        return render (request, 'coordLinea/Eventos.html', ctx)
    else:
        return redirect ('/errorLogin/')


##falta arreglar
def editEventosView (request, id_evento):
    revisarRol(request)
    try:
        storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
        credential = storage.get()
        http= httplib2.Http()
        http= credential.authorize(http)
        service = build('calendar', 'v3', http=http)
    except:
        return redirect('/logout/')
    evento = Evento.objects.get(id=id_evento)
    if request.method == 'GET':
        form = AgregarEventoForm(initial={
                'summary' : evento.summary,
                'location' : evento.location,
                'descripcion' : evento.descripcion,
                'tipoEvento' : evento.tipoEvento,
                'start': evento.start,
                'end': evento.end })
    if request.method == 'POST':
        form = AgregarEventoForm(request.POST)
        if form.is_valid():
            summary = form.cleaned_data['summary']
            location = form.cleaned_data['location']
            descripcion = form.cleaned_data['descripcion']
            tipoEvento = form.cleaned_data['tipoEvento']
            start = form.cleaned_data['start']
            start = build_rfc3339_phrase(start)
            end = form.cleaned_data['end']
            end = build_rfc3339_phrase(end)
            if tipoEvento == 'general' :
                todos = User.objects.all()
                idCal = evento.id_calendar
                eventt = service.events().get(calendarId='primary', eventId=idCal).execute()
                event = {
                    'summary': '%s'%(summary),
 
                    'start': {
                        'dateTime': '%s'%(start),
                        # 'timeZone': 'America/Santiago'
                      },
                    'end': {
                        'dateTime': '%s'%(end),
                        # 'timeZone': 'America/Santiago'
                      }
                                    }                                 
                event['attendees']= [{'email': 'gabriela.leon@usach.cl'}]
                event['attendees']= [{'email': 'gabi.leon.f@usach.cl'}]
                idCal = evento.id_calendar
                updated_event = service.events().update(calendarId='primary', eventId=idCal, body=event).execute()
                
                evento.summary= summary 
                evento.location = location
                evento.start =start
                evento.end=end
                evento.descripcion=descripcion 
                # evento.attendees=emails
                evento.tipoEvento = tipoEvento
                evento.save()
            if tipoEvento == 'coordinadores':
                idCal = evento.id_calendar
                eventt = service.events().get(calendarId='primary', eventId=idCal).execute()
                linea = Linea.objects.get(nombreLinea = 'Proyectos')
                coordinador = linea.coordinador.email
                event = {
                    'summary': '%s'%(summary),
 
                    'start': {
                        'dateTime': '%s'%(start),
                        # 'timeZone': 'America/Santiago'
                      },
                    'end': {
                        'dateTime': '%s'%(end),
                        # 'timeZone': 'America/Santiago'
                      }}
                event['attendees'] =  [{'email': coordinador}]
                idCal = evento.id_calendar
                event = service.events().get(calendarId='primary', eventId=idCal).execute()
                updated_event = service.events().update(calendarId='primary', eventId=eventt['id'], body=event).execute()
                evento.summary= summary 
                evento.location = location
                evento.start =start
                evento.end=end
                evento.descripcion=descripcion 
                evento.attendees=emails
                evento.tipoEvento = tipoEvento
                evento.save()
        return redirect('/crearFechasCord/')
    return render(request, 'coordLinea/editEvents.html', {'form':form, 'evento': evento, 'invitados' : invitados})

def deleteFechasCordView (request, id_evento):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        try:
            storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
            credential = storage.get()
            http= httplib2.Http()
            http= credential.authorize(http)
            service = build('calendar', 'v3', http=http)
        except:
            return redirect('/logout/')
        evento  = Evento.objects.get(id=id_evento)
        service.events().delete(calendarId='primary', eventId=evento.id_calendar).execute()
        evento.delete()
        return redirect('/crearFechasCord/')
    else:
        return redirect ('/errorLogin/')
      
def otroPerfilView(request, id_user):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        actual = request.user
        userTemp = User.objects.get(id =id_user)
        perfil = UserProfile.objects.get(user=userTemp.id)
        ctx = {'user': userTemp, 'perfil': perfil, 'actual':actual}
        return render(request, 'presentacion/perfil.html', ctx)
    else:
        return redirect ('/errorLogin/')

def recursosCordView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        Recursos = Recurso.objects.filter(creador=request.user)
        jefe = UserProfile.objects.get(rol_JC='JC')
        recursosJefe = Recurso.objects.filter(creador=jefe.user)
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                # handle_uploaded_file(request.FILES['file'])
                ###### el nombre dle recurso no debe tener espacios
                recurso = form.cleaned_data['recurso']            
                titulo_recurso = form.cleaned_data['title']
                descripcion = form.cleaned_data['descripcion']
                estado = form.cleaned_data['estado']
                fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
                newRecurso = Recurso.objects.create(recurso = recurso, creador=request.user, titulo_recurso=titulo_recurso, descripcion_recurso=descripcion, estado=estado, fechaUltimaModificacion=fechaUltimaModificacion)
                newRecurso.save()
                return HttpResponseRedirect('/recursosCord/')
        else:
            form = UploadFileForm()
        ctx = {'form': form, 'recursos': Recursos, 'username': request.user.username, 'recursosJefe': recursosJefe}
        return render(request, 'coordLinea/recursos.html', ctx)
    else:
        return redirect ('/errorLogin/')


def deleteRecursoView(request, id_recurso):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        Recursos = Recurso.objects.get(id=id_recurso)
        Recursos.delete()
        return HttpResponseRedirect('/recursos/')
    else:
        return redirect ('/errorLogin/')

def editRecursosView(request, id_recurso):
    # recurs = Recurso.objects.get(id=id_recurso)
    # if request.method == 'GET':
    #     form = UploadFileForm(initial={
    #             'recurso' : recurs.recurso,
    #             'title' : recurs.titulo_recurso,
    #             'descripcion' : recurs.descripcion_recurso,
    #             'estado' : recurs.estado})
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        Recursos = Recurso.objects.get(id=id_recurso)
        if request.method == 'GET':
            form = UploadFileForm(initial={
                'recurso' : Recursos.recurso,
                'title' : Recursos.titulo_recurso,
                'descripcion' : Recursos.descripcion_recurso,
                'estado' : Recursos.estado})
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                # Recursos = Recurso.objects.get(id=id_recurso)
                # Recursos.delete()
                recurso = form.cleaned_data['recurso']            
                titulo_recurso = form.cleaned_data['title']
                descripcion = form.cleaned_data['descripcion']
                estado = form.cleaned_data['estado']
                fechaUltimaModificacion = datetime.now() -timedelta(hours=3)

                Recursos.recurso = recurso            
                Recursos.titulo_recurso = titulo_recurso
                Recursos.descripcion = descripcion
                Recursos.estado = estado
                Recursos.fechaUltimaModificacion = fechaUltimaModificacion
                Recursos.save()
            return redirect('/recursos/')
        return render(request, 'jefeCarrera/editRecursos.html', {'form': form})
    else:
        return redirect ('/errorLogin/') 

def aprobadosCordViews(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        programas = Programa.objects.filter(state="fin")
        username = request.user.username
        ctx = {'username': username, 'programas': programas}
        return render (request, 'coordLinea/progAprobados.html', ctx)
    else:
        return redirect ('/errorLogin/')

###################### Fast Track #############################
def analizarCordViews (request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        programas = Programa.objects.filter(state="fastTrack")
        username = request.user.username
        ctx = {'username': username, 'programas': programas}
        return render (request, 'coordLinea/progPorAnalizarFT.html', ctx)
    else:
        return redirect ('/errorLogin/')

################# AProbacion Linea ########################

def preAnalisisCordView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        programas = Programa.objects.filter(state="aprobacionLinea")
        analisis = []
        for p in programas:
            if p.analisism.votoEvalCord==False:
                analisis.append(p)
        username = request.user.username
        form = analisisLineaForm() 
        ctx = {'username': username, 'programas': analisis, 'form': form}
        return render (request, 'coordLinea/votacionesAnalisis.html', ctx)
    else:
        return redirect ('/errorLogin/')

############# FORM Y PROCESO DE VOTACION ANALISIS DEL COORDINADOR ############
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

def votacionCordAnalisis (request, id_programa):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
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
                analisis.votoEvalCord = True
                analisis.save()
                analisisVot(analisis)
                return redirect('/programasPorAnalizarLinea/')
    else:
        return redirect ('/errorLogin/')

########### FIN ##################3

def logCordView(request, id_programa):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'CL':
        log = Log.objects.filter(programa = id_programa).order_by('-fecha')
        ctx = {'username': request.user.username, 'log': log}
        return render (request, 'coordLinea/log.html', ctx)
    else:
        return redirect ('/errorLogin/')

            

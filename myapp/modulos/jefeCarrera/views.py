from django.shortcuts import render, redirect, render_to_response, get_object_or_404
import datetime, random, sha
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from myapp.modulos.presentacion.models import UserProfile
from myapp.modulos.formulacion.models import Log, Profesor, Programa, MyWorkflow,  ClaseClase, Linea, Asignatura, Recurso
from myapp.modulos.presentacion.forms import ImageUploadForm
from myapp.modulos.jefeCarrera.models import Evento, ReporteIndic
from myapp.modulos.coordLinea.forms import CoordinadorForm
from myapp.modulos.formulacion.forms import LineasForm, UploadFileForm, analizarForm
from myapp.modulos.jefeCarrera.forms import changePasswordForm, AgregarEventoForm,  agregarAsignaturaForm, agregarProfesoresForm
from datetime import datetime, timedelta
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

# Create your views here.

def revisarRol (request):
    user = User.objects.get(username=request.user.username)
    perfil = UserProfile.objects.get(user=user.id)
    bandera = None
    if perfil.rol_actual == 'JC':
        pass
    else:
        return redirect ('/errorLogin/')


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive' ' https://www.googleapis.com/auth/calendar ',
    redirect_uri=settings.REDIRECT_URI)


def RolView(request, id_user):
    user = User.objects.get(id=id_user)
    perfil = UserProfile.objects.get(user=user.id)
    ### Si tiene un unico rol, entra directo
    return render(request, 'presentacion/cambiarRol.html', {'user':user, 'perfil':perfil, 'username':request.user.username, 'rol': perfil.rol_actual})

def cambiarRolView(request, id_user, rol):
    user = User.objects.get(id=id_user)
    perfil = UserProfile.objects.get(user=user.id)
    if rol == 'PL':
        perfil.rol_actual = 'PL'
        perfil.save()
        if perfil.fechaPrimerAcceso is None:
            return redirect('/cambiarDatosProfe/')
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

def principalView(request):
    user = User.objects.get(username=request.user.username)
    perfil = UserProfile.objects.get(user=user.id)
    if perfil.rol_actual == 'JC':
        programa = Programa.objects.all().order_by('-fechaUltimaModificacion')
        programasAprobados= Programa.objects.filter(state='fin').count()
        programasPorAprobar= Programa.objects.filter(state='aprobacionProgramaJC').count()
        programasPorAnalizar= Programa.objects.filter(state='analisisProgramaJC').count()
        username = request.user.username
        userTemp = User.objects.get(username=request.user.username)
        ctx = {'user': userTemp, 'username' : username, 'programas':programa, 'aprobados' : programasAprobados, 'aprobar': programasPorAprobar, 'analizar':programasPorAnalizar}
        return render(request, 'jefeCarrera/vistaJC.html', ctx)
    else:
        return redirect ('/errorLogin/')

def changePasswordView(request, id_user):
    u = User.objects.get(id=id_user)
    form = changePasswordForm()
    username = u.username
    if request.method == "POST":
        form = changePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            password = form.cleaned_data['password']
            if u is not None and u.check_password(old_password):
                u.set_password(password)
                u.save()
                return HttpResponseRedirect("/miperfil/")
    ctx = {'form':form, 'user':u, 'username': username}
    return render(request, 'presentacion/changePassword.html', ctx)

def miperfilView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        ctx = {'user': userTemp, 'perfil': perfilTemp, 'username': request.user.username}
        if request.method == 'POST':
            form = ImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                foto = form.cleaned_data['image']
                perfilTemp.foto = foto 
                perfilTemp.save()
                return redirect('/miperfil/')
        return render(request, 'jefeCarrera/perfilConf.html', ctx)
    else:
        return redirect ('/errorLogin/')

def lineasView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        linea = Linea.objects.all()
        form = LineasForm()
        if request.method == "POST":
            form = LineasForm(request.POST)
            if form.is_valid():
                nombreLinea = form.cleaned_data['nombreLinea']
                linea = Linea.objects.create(nombreLinea= nombreLinea)
                carpeta = "Linea de " + nombreLinea
                ### Crear Carpeta #####drive
                try:
                    storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
                    credential = storage.get()
                    http= httplib2.Http()
                    http= credential.authorize(http)
                    drive_service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
                except:
                    return redirect('/logout/')
                body2 = {
                           'title': '%s'%carpeta,
                           'mimeType': "application/vnd.google-apps.folder"
                       }
                       ### se crea carpeta ###
                folder = drive_service.files().insert(body = body2).execute()
                id_folder = folder.get('id')
                linea.carpeta = id_folder
                linea.save()
                return HttpResponseRedirect("/lineas/")
        ctx = {'form':form, 'linea':linea, 'username': request.user.username}
        return render(request, 'jefeCarrera/lineaConf.html', ctx)
    else:
        return redirect ('/errorLogin/')

def perfilLineaView(request, id_linea):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        linea = Linea.objects.get(id=id_linea)
        asignaturas = Asignatura.objects.filter(linea=linea)
        profesores = Profesor.objects.filter(linea=linea)
        estado = 0
        # profesores = Profesor.objects.filter(linea__id=id_linea)
        form = CoordinadorForm()
        if request.method == "POST":
            form = CoordinadorForm(request.POST)
            if form.is_valid():
                coordinador = form.cleaned_data['coordinador']
                try:
                   x = User.objects.get(email=coordinador)
                except User.DoesNotExist:
                   x = None
                if  x is None:
                    #crear un usuario nuevo, con su perfil y con rol CL
                    #llamar a la funcion que crea nombres de usuario
                    username = coordinador.split("@", 1)
                    newUser = User.objects.create(email=coordinador, username=username[0])
                    newUser.set_password(username[0])
                    newUser.save()
                    userProfile = UserProfile.objects.create(rol_CL='CL', user=newUser, cordLinea= linea, fechaPrimerAcceso = None)
                    linea.coordinador= newUser
                    linea.save()
                    userProfile.save()
                    ## se envia email al nuevo coordinador ##
                    message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",
                          subject="Notificacion")

                    message.to = coordinador
                    # html_content = " Estimado:<br><br><br> ha sido designado como Coordinador de la linea" 
                    # +linea.nombreLinea + ". Para la realizacion de esta funcion se necesitara que usted acceda a http://programas-diinf.appspot.com/login con su username y password"+username[0]". Al ingresar debera actualizar sus datos. Saludos"
                    # message.send()

                # Comprobar si existe el coordinador en el sistema
                else:
                    temp = User.objects.get(email=coordinador)
                    profile = UserProfile.objects.get(user=temp.id)
                    profile.rol_CL = 'CL'
                    profile.cordLinea = linea
                    profile.save()
                    linea.coordinador = temp
                    linea.save()
                    message = mail.EmailMessage(sender="Administrador <gabi.leon.f@gmail.com>",
                        subject="Notificacion")

                    message.to = coordinador
                    # message.html " Estimado:<br><br><br> ha sido designado como Coordinador de la linea" 
                    #  +linea.nombreLinea + ". Al ingresar a http://programas-diinf.appspot.com/login tendra acceso a entrar al rol del Coordinador de Linea. Saludos."
                    # message.send()
                                        

            return HttpResponseRedirect('/perfilLinea/'+id_linea)   
        else:
            form = CoordinadorForm()
        ctx = {'form':form, 'linea':linea, 'estado':estado, 'username': request.user.username, 'asignaturas' : asignaturas, 'linea':linea, 'profesores': profesores}
        return render(request, 'jefeCarrera/perfilLineaConf.html', ctx)
    else:
        return redirect ('/errorLogin/')

def removeCordinadorLineaView(request, id_linea):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        linea = Linea.objects.get(id=id_linea)
        cordinador = linea.coordinador
        cordinador.userprofile.rol_CL = "hola"
        cordinador.save()
        linea.coordinador = None
        linea.save()
        return HttpResponseRedirect('/perfilLinea/'+id_linea)   
    else:
        return redirect ('/errorLogin/')

def addAsignaturaView(request, id_linea):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        linea = Linea.objects.get(id=id_linea)
        form = agregarAsignaturaForm()
        if request.method == "POST":
            form = agregarAsignaturaForm(request.POST)
            if form.is_valid():
                asignatura = form.cleaned_data['nombreAsignatura']
                plan = form.cleaned_data['plan']
                try:
                    asig = Asignatura.objects.get(nombreAsig=asignatura)
                except:
                    asig = None
                if asig is not None:
                    asig.linea = linea
                    asig.save()
                else:
                    nuevaAsig = Asignatura.objects.create(nombreAsig=asignatura, plan = plan, linea=linea)
                    nuevaAsig.save()
                return HttpResponseRedirect('/perfilLinea/'+id_linea)
        else:
            form = agregarAsignaturaForm()
            
        ctx ={'form' :form, 'linea':linea, 'username': request.user.username}
        return render(request, 'jefeCarrera/addAsignatura.html', ctx)
    else:
        return redirect ('/errorLogin/')

def removeAsignaturaView(request, id_asignatura, id_linea):
    asignatura = Asignatura.objects.get(id=id_asignatura)
    asignatura.linea = None
    asignatura.save()
    return HttpResponseRedirect('/perfilLinea/'+id_linea)
    
def crearFechas(request):
    status = ""
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    hoy = datetime.now()
    if perfilTemp.rol_actual == 'JC':
        eventos = Evento.objects.filter(anfitrion=request.user).order_by('-start').filter(start__range=(hoy - timedelta(days=1), hoy + timedelta(days=200)))
        eventosInvitados = Evento.objects.filter(tipoEvento='jefe').order_by('-start').filter(start__range=(hoy - timedelta(days=1), hoy + timedelta(days=200)))
        try:
            storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
            credential = storage.get()
            http= httplib2.Http()
            http= credential.authorize(http)
            service = build('calendar', 'v3', http=http)
            calendar_list_entry = service.calendarList().get(calendarId='primary').execute()
        except:
            return redirect('/errorGoogle/')
        form = AgregarEventoForm()
        if request.method == 'POST':
            form = AgregarEventoForm(request.POST)
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
                if tipoEvento == 'general' :
                    todos = User.objects.all()
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
                    for email in todos:
                        x = {}
                        x.update({'email': email.email})
                        invitados.append(email.email)
                        emails.append(x)

                    event.update({'attendees': emails})
                    try:
                        created_event = service.events().insert(calendarId='primary', body=event).execute()
                        nuevoEvento = Evento.objects.create(summary= summary, location = location, start =start, end=end, 
                        descripcion=descripcion, id_calendar=created_event['id'], tipoEvento=tipoEvento, anfitrion=request.user, invitados =invitados)
                        nuevoEvento.save()
                    except:
                        ('/errorGoogle/')         

                if tipoEvento == 'coordinadores':
                    linea = Linea.objects.get(nombreLinea = 'Proyectos')
                    coordinador = linea.coordinador.email
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
                    event['attendees'] =  [{'email': coordinador}]
                    try:
                        created_event = service.events().insert(calendarId='primary', body=event).execute()
                        nuevoEvento = Evento.objects.create(summary= summary, location = location, start =start, end=end, 
                        descripcion=descripcion,  id_calendar=created_event['id'], tipoEvento=tipoEvento , anfitrion=request.user, invitados =coordinador)
                        nuevoEvento.save()
                    except:
                        ('/errorGoogle/')                            
            else:
                status = "Completar todos los campos"
        else:
            form = AgregarEventoForm()
        ctx = {'form':form, 'eventos': eventos, 'status': status, 'username': request.user.username, 'eventosInvitados': eventosInvitados}
        return render (request, 'jefeCarrera/Eventos.html', ctx)
    else:
        return redirect ('/errorLogin/')

def editEventosView (request, id_evento):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
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
                inicio = build_rfc3339_phrase(start)
                end = form.cleaned_data['end']
                fin = build_rfc3339_phrase(end)
                if tipoEvento == 'general' :
                    todos = User.objects.all()
                    idCal = evento.id_calendar
                    eventt = service.events().get(calendarId='primary', eventId=idCal).execute()
                    event = {
                        'summary': '%s'%(summary),
     
                        'start': {
                            'dateTime': '%s'%(inicio),
                           
                          },
                        'end': {
                            'dateTime': '%s'%(fin),
                            
                          }
                                        }                                 
                    invitados = []
                    emails  = []
                    for email in todos:
                        x = {}
                        x.update({'email': email.email})
                        invitados.append(email.email)
                        emails.append(x)

                    event.update({'attendees': emails})
                    idCal = evento.id_calendar
                    updated_event = service.events().update(calendarId='primary', eventId=idCal, body=event).execute()
                    evento.summary= summary 
                    evento.location = location
                    evento.start =start
                    evento.end=end
                    evento.descripcion=descripcion 
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
                            'dateTime': '%s'%(inicio),
                          },
                        'end': {
                            'dateTime': '%s'%(fin),
                          }}
                    event['attendees'] =  [{'email': coordinador}]
                    event = service.events().get(calendarId='primary', eventId=idCal).execute()
                    updated_event = service.events().update(calendarId='primary', eventId=eventt['id'], body=event).execute()
                    evento.summary= summary 
                    evento.location = location
                    evento.start =start
                    evento.end=end
                    evento.descripcion=descripcion 
                    evento.attendees=coordinador
                    evento.tipoEvento = tipoEvento
                    evento.save()
            return redirect('/crearFechas/')
        return render(request, 'jefeCarrera/editEvents.html', {'form':form, 'evento': evento, 'username':request.user.username})
    else:
        return redirect ('/errorLogin/')

def deleteFechasView (request, id_evento):
    try:
        storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
        credential = storage.get()
        http= httplib2.Http()
        http= credential.authorize(http)
        service = build('calendar', 'v3', http=http)
    except:
        return redirect('/logout/')
    # First retrieve the event from the API.
    evento  = Evento.objects.get(id=id_evento)
    service.events().delete(calendarId='primary', eventId=evento.id_calendar).execute()
    evento.delete()
    return redirect('/crearFechas/')

def logJCView(request, id_programa):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        log = Log.objects.filter(programa = id_programa).order_by('-fecha')
        ctx = {'username': request.user.username, 'log': log}
        return render (request, 'jefeCarrera/log.html', ctx)
    else:
        return redirect ('/errorLogin/')

   
def otroPerfilView(request, id_user):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        actual = request.user
        userTemp = User.objects.get(id =id_user)
        perfil = UserProfile.objects.get(user=userTemp.id)
        ctx = {'user': userTemp, 'perfil': perfil, 'actual':actual}
        return render(request, 'presentacion/perfil.html', ctx)
    else:
        return redirect ('/errorLogin/')

def recursosView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        Recursos = Recurso.objects.all()
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                ###### el nombre dle recurso no debe tener espacios
                recurso = form.cleaned_data['recurso']            
                titulo_recurso = form.cleaned_data['title']
                descripcion = form.cleaned_data['descripcion']
                estado = form.cleaned_data['estado']
                fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
                newRecurso = Recurso.objects.create(recurso = recurso, titulo_recurso=titulo_recurso, creador=request.user, descripcion_recurso=descripcion, estado=estado, fechaUltimaModificacion=fechaUltimaModificacion)
                newRecurso.save()
                return HttpResponseRedirect('/recursos/')
        else:
            form = UploadFileForm()
        ctx = {'form': form, 'recursos': Recursos, 'username': request.user.username}
        return render(request, 'jefeCarrera/recursos.html', ctx)
    else:
        return redirect ('/errorLogin/')

def deleteRecursoView(request, id_recurso):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        Recursos = Recurso.objects.get(id=id_recurso)
        Recursos.delete()
        return HttpResponseRedirect('/recursos/')
    else:
        return redirect ('/errorLogin/')

def editRecursosView(request, id_recurso):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        recursos = Recurso.objects.get(id=id_recurso)
        if request.method == 'GET':
            form = UploadFileForm(initial={
                'recurso' : recursos.recurso,
                'title' : recursos.titulo_recurso,
                'descripcion' : recursos.descripcion_recurso,
                'estado' : recursos.estado})
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                recurso = form.cleaned_data['recurso']            
                titulo_recurso = form.cleaned_data['title']
                descripcion = form.cleaned_data['descripcion']
                estado = form.cleaned_data['estado']
                fechaUltimaModificacion = datetime.now() - timedelta(hours=3)
                recursos.recurso = recurso            
                recursos.titulo_recurso = titulo_recurso
                recursos.descripcion_recurso = descripcion
                recursos.estado = estado
                recursos.fechaUltimaModificacion = fechaUltimaModificacion
                recursos.save()
            return redirect('/recursos/')
        return render(request, 'jefeCarrera/editRecursos.html', {'form': form})
    else:
        return redirect ('/errorLogin/')

def aprobadosViews(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        programas = Programa.objects.filter(state="fin")
        username = request.user.username
        ctx = {'username': username, 'programas': programas}
        return render (request, 'formulacion/progAprobados.html', ctx)
    else:
        return redirect ('/errorLogin/')

def porAnalizarViews(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        programas = Programa.objects.filter(state="analisisProgramaJC")
        username = request.user.username
        ctx = {'username': username, 'programas': programas}
        return render (request, 'formulacion/programasAnalizar.html', ctx)
    else:
        return redirect ('/errorLogin/')

def reportesIndicacionView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        reportes = ReporteIndic.objects.all()
        return render(request, 'jefeCarrera/reportesIndicaciones.html', {'reportes':reportes, 'username': request.user.username})
    else:
        return redirect ('/errorLogin/')

def analisisProgramaView(request, id_programa, decision):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        programa = Programa.objects.get(id=id_programa)
        id_p = programa.id
        ## Si hay indicaciones
        if decision == 'yes':
            # Revisa el indicador, 
            try:
                m = ProgramasPorEstado.objects.get(estado=programa.state.title)
            except ProgramasPorEstado.DoesNotExist:
                m = None
                # Si no existe
            if m is None:
                #crea un nuevo indicador
                newIndicador = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
                newIndicador.save()
                #si existe
            else:
                m.cantidad = m.cantidad - 1
                m.save()
                #programa pasa a formulacion
                programa.siIndic_toForm()
                logEstado(programa, programa.state.title)
                programa.to_datosAsig()
                logEstado(programa, programa.state.title)
                programa.save()
                # se ve si existe el indicador para el estado del siguiente estado
                try:
                    n = ProgramasPorEstado.objects.get(estado=programa.state.title)
                except ProgramasPorEstado.DoesNotExist:
                    n = None
                if n is None:
                    newIndicador2 = ProgramasPorEstado.objects.create(estado=programa.state.title, cantidad=1)
                    newIndicador2.save()
                else:
                    n.cantidad = n.cantidad + 1
                    n.save()
            ## se crea la carpeta
            perfil = UserProfile.objects.get(user=request.user)
            try:
                carpeta = perfil.carpetaReportes
            except:
                carpeta = None
            if carpeta is None:
                carpeta = 'Reporte de Indicaciones'
                reporte = ReporteIndic()
                reporte.programa = programa
                try:
                    storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
                    credential = storage.get()
                    http= httplib2.Http()
                    http= credential.authorize(http)
                    drive_service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
                except:
                    return redirect('/logout/')
                body2 = {
                           'title': '%s'%carpeta,
                           'mimeType': "application/vnd.google-apps.folder"
                       }
                       ### se crea carpeta ###
                folder = drive_service.files().insert(body = body2).execute()
                id_folder = folder.get('id')
                titulo = "Reporte de Indicaciones Programa " + programa.asignatura.nombreAsig + " " + programa.semestre + " " + programa.ano
                body = {
                    'title':'%s'%(titulo),
                    'mimeType': "application/vnd.google-apps.document",
                    'parents' : [{'id' : id_folder}]
                }                       
                try:
                    file = drive_service.files().insert(body=body).execute()
                    url = file.get('alternateLink')
                    reporte.url = url
                    reporte.fechaModificacion=datetime.now()
                    reporte.carpeta = id_folder
                    perfil.carpetaReportes = id_folder
                    perfil.save()
                    reporte.save()
                except:
                    return render(request, 'comunicacion/error.html')
            else:
                reporte = ReporteIndic()
                reporte.programa = programa
                reporte.carpeta = carpeta
                try:
                    storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
                    credential = storage.get()
                    http= httplib2.Http()
                    http= credential.authorize(http)
                    drive_service = build('drive', 'v2', http=http, developerKey="hbP6_4UJIKe-m74yLd8tQDfT")
                except:
                    return redirect('/logout/')
                titulo = "Reporte de Indicaciones Programa " + programa.asignatura.nombreAsig + " " + programa.semestre + " " + programa.ano
                body = {
                    'title':'%s'%(titulo),
                    'mimeType': "application/vnd.google-apps.document",
                    'parents' : [{'id' : reporte.carpeta}]
                }                       
                try:
                    file = drive_service.files().insert(body=body).execute()
                    url = file.get('alternateLink')
                    reporte.url = url
                    reporte.fechaModificacion=datetime.now()
                    reporte.save()
                except:
                    return render(request, 'comunicacion/error.html')
            return HttpResponseRedirect('/reportesIndicacion/')
                 
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
                programa.noIndic_toAprobJC()
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
                    n.cantidad = n.cantidad + 1
                    n.save()
            return HttpResponseRedirect('/programasPorAnalizar/')
    else:
        return redirect ('/errorLogin/')

def porAprobarView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        programas = Programa.objects.filter(state="aprobacionProgramaJC")
        username = request.user.username
        ctx = {'username': username, 'programas': programas}
        return render (request, 'formulacion/programasPorAprobar.html', ctx)
    else:
        return redirect ('/errorLogin/')

def aprobacionProgramaView(request, id_programa, decision):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
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
                programa.siAprob_toFin()
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
            else:
                m.cantidad = m.cantidad - 1
                m.save()
                programa.noAprobJC_toForm()
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
        return HttpResponseRedirect('/programasPorAprobar/')
    else:
        return redirect ('/errorLogin/')
    
def addProfesoresView(request, id_linea):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    if perfilTemp.rol_actual == 'JC':
        linea = Linea.objects.get(id=id_linea)
        form = agregarProfesoresForm()
        if request.method == 'POST':
            form = agregarProfesoresForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                try:
                   x = User.objects.get(email=email)
                except User.DoesNotExist:
                   x = None
                if  x is None:
                    #crear un usuario nuevo, con su perfil y con rol pl
                    #llamar a la funcion que crea nombres de usuario
                    username = email.split("@", 1)
                    newUser = User.objects.create(email=email, username=username[0])
                    newUser.set_password(username[0])
                    newUser.save()
                    userProfile = UserProfile.objects.create(user=newUser)
                    userProfile.rol_PL = "PL"
                    userProfile.save()
                    profe = Profesor.objects.create(user=newUser, linea=linea)
                    profe.save()
                    newUser.save()
                else:
                    x.userprofile.rol_PL = "PL"
                    x.userprofile.save()
                    try:
                        y = Profesor.objects.get(user=x)
                    except Profesor.DoesNotExist:
                        y = None
                    if  y is None:
                        profe = Profesor.objects.create(user=x, linea=linea)
                        profile = UserProfile.objects.get(user=x)
                        if profile.rol_PL!="PL":
                            profile.rol_PL= "PL"
                        profe.save()
                        profile.save()
                    else:
                        y.linea = linea
                        y.save()                        
                return HttpResponseRedirect('/perfilLinea/'+id_linea)
        asignaturas = Asignatura.objects.filter(linea=linea)
        profesores = Profesor.objects.filter(linea=linea)

        ctx = {'form':form, 'linea':linea, 'asignaturas':asignaturas, 'profesores':profesores, 'username': request.user.username}
        return render(request, 'jefeCarrera/addProf.html', ctx)
    else:
        return redirect ('/errorLogin/')

def removeProfesorLineaView(request, id_user, id_linea):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    profesor = Profesor.objects.get(user=id_user)

    if perfilTemp.rol_actual == 'JC':
        profesor.linea = None
        userProf = User.objects.get(id=id_user)
        userProf.userprofile.rol_PL = ""
        userProf.userprofile.save()
        profesor.save()
        return HttpResponseRedirect('/perfilLinea/'+id_linea)   
    else:
        return redirect ('/errorLogin/')

def logEstado (programa, state):
    l= Log()
    l.programa = programa
    l.state = state
    l.fecha = datetime.now() - timedelta(hours=3)
    l.save()    
            

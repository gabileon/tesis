from django.shortcuts import render, redirect
import datetime, random, sha
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from myapp.modulos.presentacion.models import UserProfile
from myapp.modulos.formulacion.models import Programa, MyWorkflow, Objetivo, Capacidad, Contenido, ClaseClase, Linea, Asignatura, Recurso
from myapp.modulos.presentacion.forms import ImageUploadForm
from myapp.modulos.jefeCarrera.models import Evento
from myapp.modulos.coordLinea.forms import CoordinadorForm
from myapp.modulos.formulacion.forms import LineasForm, UploadFileForm, analizarForm
from myapp.modulos.jefeCarrera.forms import AgregarEventoForm,  agregarAsignaturaForm
from datetime import datetime
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
from myapp.modulos.jefeCarrera.rfc3339 import rfc3339

# Create your views here.

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
FLOW = flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive' ' https://www.googleapis.com/auth/calendar',
    redirect_uri=settings.REDIRECT_URI)


def principalView(request):
    programa = Programa.objects.all().order_by('-fechaUltimaModificacion')
    programasAprobados= Programa.objects.filter(state='fin').count()
    programasPorAprobar= Programa.objects.filter(state='aprobacionProgramaJC').count()
    programasPorAnalizar= Programa.objects.filter(state='analisisProgramaJC').count()
    username = request.user.username
    ctx = {'username' : username, 'programas':programa, 'aprobados' : programasAprobados, 'aprobar': programasPorAprobar, 'analizar':programasPorAnalizar}
    return render(request, 'jefeCarrera/vistaJC.html', ctx)

def miperfilView(request):
    userTemp = User.objects.get(username=request.user.username)
    perfilTemp = UserProfile.objects.get(user=userTemp.id)
    ctx = {'user': userTemp, 'perfil': perfilTemp}
    
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            foto = form.cleaned_data['image']
            perfilTemp.foto = foto 
            perfilTemp.save()
            return redirect('/miperfil/')
    return render(request, 'jefeCarrera/perfilConf.html', ctx)

def lineasView(request):
    linea = Linea.objects.all()
    form = LineasForm()
    if request.method == "POST":
        form = LineasForm(request.POST)
        if form.is_valid():
            nombreLinea = form.cleaned_data['nombreLinea']
            linea = Linea.objects.create(nombreLinea= nombreLinea)
            linea.save()
            return HttpResponseRedirect("/lineas/")
    ctx = {'form':form, 'linea':linea}
    return render(request, 'jefeCarrera/lineaConf.html', ctx)

def perfilLineaView(request, id_linea):
    linea = Linea.objects.get(id=id_linea)
    asignaturas = Asignatura.objects.filter(linea=linea)
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
                newUser = User.objects.create(email=coordinador, username=username[0], password=username[0])
                userProfile = UserProfile.objects.create(rol='CL', user=newUser, cordLinea= linea)
                linea.coordinador= newUser
                linea.save()
                userProfile.save()
                # to_admin = coordinador
                # html_content = " Estimado:<br><br><br> ha sido designado como Coordinador de la linea"
                # # html_content = " Estimado:<br><br><br> ha sido designado como Coordinador de la linea" +linea.nombreLinea + ". Para la realizacion de esta funcion se necesitara que usted acceda a http://programas-diinf.appspot.com/login con los siguientes datos:<br><br> username= " + username + "<br>password= " + username + ". Al ingresar debera actualziar sus datos. Saludos" 
                # msg = EmailMultiAlternatives('Coordinador de Linea', html_content,'from@server.com', [to_admin] )
                # msg.attach_alternative(html_content,'text/html')
                # msg.send()
            # Comprobar si existe el coordinador en el sistema
            else:
                temp = User.objects.get(email=coordinador)
                profile = UserProfile.objects.get(user=temp.id)
                profile.cordLinea = linea
                profile.save()
                linea.coordinador = temp
                linea.save()
        return HttpResponseRedirect('/perfilLinea/'+id_linea)   
    else:
        form = CoordinadorForm()
    ctx = {'form':form, 'linea':linea, 'estado':estado, 'asignaturas' : asignaturas, 'linea':linea}
    return render(request, 'jefeCarrera/perfilLineaConf.html', ctx)

def removeCordinadorLineaView(request, id_linea):
    linea = Linea.objects.get(id=id_linea)
    linea.coordinador = None
    linea.save()
    return HttpResponseRedirect('/perfilLinea/'+id_linea)   
    # return HttpResponse('deleted')

def addAsignaturaView(request, id_linea):
    linea = Linea.objects.get(id=id_linea)
    form = agregarAsignaturaForm()
    if request.method == "POST":
        form = agregarAsignaturaForm(request.POST)
        if form.is_valid():
            asignatura = form.cleaned_data['nombreAsignatura']
            plan = form.cleaned_data['plan']
            nuevaAsig = Asignatura.objects.create(nombreAsig=asignatura, plan = plan, linea=linea)
            nuevaAsig.save()
            return HttpResponseRedirect('/perfilLinea/'+id_linea)
    else:
        form = agregarAsignaturaForm()
        
    ctx ={'form' :form, 'linea':linea}
    return render(request, 'jefeCarrera/addAsignatura.html', ctx)

def crearFechas(request):
    eventos = Evento.objects.all()
    try:
        storage = Storage(CredentialsModel, 'id_user', request.user, 'credential')
        credential = storage.get()
        http= httplib2.Http()
        http= credential.authorize(http)
        service = build('calendar', 'v3', http=http)
    except:
        return redirect('/logout/')

    calendar_list_entry = service.calendarList().get(calendarId='primary').execute()
    form = AgregarEventoForm()
    if request.method == 'POST':
        form = AgregarEventoForm(request.POST)
        if form.is_valid():
            summary = form.cleaned_data['summary']
            location = form.cleaned_data['location']
            descripcion = form.cleaned_data['descripcion']
            start = form.cleaned_data['start']
            start = rfc3339(start)
            end = form.cleaned_data['end']
            end = rfc3339(end)
            event = {
            'summary': '%s'%(summary),
            'location': '%s'%(location),
            'start': {
                'dateTime': '%s'%(start),
                # 'timeZone': 'America/Santiago'
              },
            'end': {
                'dateTime': '%s'%(end),
                # 'timeZone': 'America/Santiago'
              },
            "attendees":[               
                {
                "email":"gabi.leon.f@gmail.com"
                }]
            }                
            created_event = service.events().insert(calendarId='primary', body=event).execute()           
            nuevoEvento = Evento.objects.create(summary= summary, location = location, start =start, end=end, descripcion=descripcion)
            nuevoEvento.save()
    else:
        form = AgregarEventoForm()
    ctx = {'form':form, 'eventos': eventos, 'username': request.user.username}
    return render (request, 'jefeCarrera/Eventos.html', ctx)

def otroPerfilView(request, id_user):
    actual = request.user
    userTemp = User.objects.get(id =id_user)
    perfil = UserProfile.objects.get(user=userTemp.id)
    ctx = {'user': userTemp, 'perfil': perfil, 'actual':actual}
    return render(request, 'presentacion/perfil.html', ctx)

def recursosView(request):
    Recursos = Recurso.objects.all()
    # Recursos = Recurso.objects.all().order_by('-fechaUltimaModificacion')
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # handle_uploaded_file(request.FILES['file'])
            recurso = form.cleaned_data['recurso']            
            titulo_recurso = form.cleaned_data['title']
            descripcion = form.cleaned_data['descripcion']
            estado = form.cleaned_data['estado']
            fechaUltimaModificacion = datetime.now()
            newRecurso = Recurso.objects.create(recurso = recurso, titulo_recurso=titulo_recurso, descripcion_recurso=descripcion, estado=estado, fechaUltimaModificacion=fechaUltimaModificacion)
            newRecurso.save()
            return HttpResponseRedirect('/recursos/')
    else:
        form = UploadFileForm()
    ctx = {'form': form, 'recursos': Recursos, 'username': request.user.username}
    return render(request, 'jefeCarrera/recursos.html', ctx) 

def aprobadosViews(request):
    programas = Programa.objects.filter(state="fin")
    username = request.user.username
    ctx = {'username': username, 'programas': programas}
    return render (request, 'formulacion/progAprobados.html', ctx)

def porAnalizarViews(request):
    programas = Programa.objects.filter(state="analisisProgramaJC")
    username = request.user.username
    form = analizarForm()
    # if request.method == 'POST':
    #     form = analizarForm(request.POST)
    #     if form.is_valid():
    #         decision = form.cleaned_data['decision']
    #         if decision == 'Si':
    #             Programa

         
    ctx = {'username': username, 'programas': programas}
    return render (request, 'formulacion/programasAnalizar.html', ctx)

def porAprobarView(request):
    programas = Programa.objects.filter(state="aprobacionProgramaJC")
    username = request.user.username
    ctx = {'username': username, 'programas': programas}
    return render (request, 'formulacion/programasPorAprobar.html', ctx)

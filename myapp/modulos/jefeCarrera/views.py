from django.shortcuts import render, redirect
import datetime, random, sha
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from myapp.modulos.presentacion.models import UserProfile
from myapp.modulos.formulacion.models import Programa, MyWorkflow, Objetivo, Capacidad, Contenido, ClaseClase, Linea
from myapp.modulos.presentacion.forms import ImageUploadForm
from myapp.modulos.coordLinea.models import Coordinador
from myapp.modulos.coordLinea.forms import CoordinadorForm
from myapp.modulos.formulacion.forms import LineasForm
from datetime import datetime
from django.shortcuts import get_object_or_404
# Create your views here.


def principalView(request):
    if request.method == "GET":
        programa = Programa.objects.all().order_by('-fechaUltimaModificacion')
        programasAprobados= Programa.objects.filter(state='fin').count()
        programasPorAprobar= Programa.objects.filter(state='aprobacionProgramaJC').count()
        programasPorAnalizar= Programa.objects.filter(state='analisisProgramaJC').count()
        username = request.user.username
        ctx = {'username' : username, 'programas':programa, 'aprobados' : programasAprobados, 'aprobar': programasPorAprobar, 'analizar':programasPorAnalizar}
        return render(request, 'jefeCarrera/vistaJC.html', ctx)

def miperfilView(request):
    if request.method == "GET":
        userTemp = User.objects.get(username=request.user.username)
        perfilTemp = UserProfile.objects.get(username=userTemp.id)
        
        ctx = {'user': userTemp, 'perfil': perfilTemp}

        return render(request, 'jefeCarrera/perfilConf.html', ctx)

def upload_pic(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            userTemp = User.objects.get(username=request.user.username)
            perfilTemp = UserProfile.objects.get(username=userTemp.id)
            perfilTemp.foto = form.cleaned_data['image']
            perfilTemp.save()
            return redirect('/miperfil/')
    return HttpResponseForbidden('allowed only via POST')

def recursosView(request):
    pass
def lineasView(request):
    linea = Linea.objects.all()
    form = LineasForm()
    if request.method == "POST":
        form = LineasForm(request.POST)
        if form.is_valid():
            nombreLinea = form.cleaned_data['nombreLinea']
            # coordinador = form.cleaned_data['coordinador']
            # profesor= form.cleaned_data['profesor']
            linea = Linea.objects.create(nombreLinea= nombreLinea)
            linea.save()
            return redirect('/lineas')
        else:
            ctx = {'form':form, }
            return render(request, 'jefeCarrera/lineaConf.html', ctx)
    ctx = {'form':form, 'linea':linea}
    return render(request, 'jefeCarrera/lineaConf.html', ctx)

def perfilLineaView(request, id_linea):
    linea = Linea.objects.get(id=id_linea)
    coord = linea.coordinador
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
                #crear un usaurio nuevo, con su perfil y con rol CL
                #llamar a la funcion que crea nombres de usuario
                username = coordinador.split("@", 1)
                newUser = User.objects.create(email=coordinador, username=username[0], password=username[0])
                userProfile = UserProfile.objects.create(rol='CL', username=newUser)
                cordinadorNuevo = Coordinador.objects.create(profile=userProfile, fechaAsigna=datetime.now())
                linea.coordinador= cordinadorNuevo
                linea.save()  
            # Comprobar si existe el coordinador en el sistema
            else:
                cordProfile = UserProfile.objects.get(username=(User.objects.get(email=coordinador).id))
                cordinadorNuevo = Coordinador.objects.create(profile=cordProfile, fechaAsigna=datetime.now())
                linea.coordinador= cordinadorNuevo
                linea.save()
        else:
            ctx = {'form':form, }
            return render(request, 'jefeCarrera/perfilLineaConf.html', ctx)
    ctx = {'form':form, 'linea':linea, 'coord': coord, 'estado':estado}
    return render(request, 'jefeCarrera/perfilLineaConf.html', ctx)

def removeCordinadorLineaView(request, id_linea):
    ctx = ""
    linea = Linea.objects.get(id=id_linea)
    linea.coordinador = None
    linea.save()
    return redirect('/perfilLinea/'+id_linea)
    # return HttpResponse('deleted')


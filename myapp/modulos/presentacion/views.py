from django.shortcuts import render
from django.http import HttpResponse
from myapp.modulos.formulacion.models import Programa
from django.contrib.auth import authenticate, login
# Create your views here.



def welcome_view(request):
	status = "GABRIELA"
	ctx = {'status' : status}
	return render(request, 'presentacion/welcome.html', ctx)

def programas_view(request):
	programa = Programa.objects.all()
	#prod = producto.objects.filter(status=True) #Select "from ventas_productos where status = True"
	ctx = {'programas': programa}
	#return HttpResponse(programa)
	return render(request, 'presentacion/programas.html', ctx)

def cadaprograma_view(request, id_programa):
	programa = Programa.objects.get(id=id_programa)
	ctx = {'programa' : programa}
	return render(request, 'presentacion/ver_programa.html', ctx )

def login_view(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username=username, password=password)
	if user is not None:
		if user.is_active:
			login(request, user)
            # Redirect to a success page.
	ctx = "dklsd"
	return render(request, 'login.html', ctx)



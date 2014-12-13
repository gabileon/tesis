from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.profLinea.views',
    url(r'^principalPL/$', 'principalPLView', name='principalPL_view'),
   	url(r'^eliminarPrograma/(?P<id_programa>.*)/$', 'eliminarProgramaView' ),
   	url(r'^recursosProfe/$', 'repositorioView' ),
   	url(r'^fechasProfe/$', 'fechasView' ),
   	url(r'^cambiarDatosProfe/$', 'cambiarDatosProfeView' ),
   	url(r'^miperfilProfesor/$', 'miperfilProfesorView' ),   		

   	
)

from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.presentacion.views',
#     url(r'^$', 'welcome_view', name='vista_welcome'),
	url(r'^programas/$', 'programas_view', name= 'vista_programas'),
	url(r'^verPrograma/(?P<id_programa>.*)/$', 'cadaprograma_view'),
	url(r'^$', 'login_view'),


)
from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.presentacion.views',
#     url(r'^$', 'welcome_view', name='vista_welcome'),
	url(r'^programas/$', 'programas_view', name= 'vista_programas'),
	url(r'^verPrograma/(?P<id_programa>.*)/$', 'cadaprograma_view'),
	url(r'^login/$', 'login_view', name= 'login_view'),
	url(r'^logout/$', 'logout_view', name= 'logout_view'),
	url(r'^sign_up/$', 'signup_view', name='vista_signup'),

)
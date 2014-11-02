from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.jefeCarrera.views',
	url(r'^principal_jc/$', 'principalView', name= 'principalJC_view'),
	url(r'^miperfil/$', 'miperfilView', name= 'miperfil_view'),
	url(r'^lineas/$', 'lineasView', name= 'lineas_view'),
	url(r'^recursos/$', 'recursosView', name= 'recursos_view'),
	url(r'^upload_pic/$', 'upload_pic', name= 'upload_pic_view'),
	url(r'^perfilLinea/(?P<id_linea>.*)/$', 'perfilLineaView'),
	url(r'^removeCordinador/(?P<id_linea>.*)/$', 'removeCordinadorLineaView'),
	

)

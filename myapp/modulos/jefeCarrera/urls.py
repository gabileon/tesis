from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.jefeCarrera.views',
	url(r'^principal_jc/$', 'principalView', name= 'principalJC_view'),
	url(r'^miperfil/$', 'miperfilView', name= 'miperfil_view'),
	url(r'^lineas/$', 'lineasView', name= 'lineas_view'),
	url(r'^recursos/$', 'recursosView', name= 'recursos_view'),
	url(r'^perfilLinea/(?P<id_linea>.*)/$', 'perfilLineaView'),
	url(r'^removeCordinador/(?P<id_linea>.*)/$', 'removeCordinadorLineaView'),
	url(r'^crearFechas/$', 'crearFechas'),
	url(r'^addAsignatura/(?P<id_linea>.*)/$', 'addAsignaturaView'),
	url(r'^otroPerfil/(?P<id_user>.*)/$', 'otroPerfilView'),
	url(r'^recursos/$', 'otroPerfilView'),
	url(r'^programasAprobados/$', 'aprobadosViews'),
	url(r'^programasPorAnalizar/$', 'porAnalizarViews'),
	url(r'^programasPorAprobar/$', 'porAprobarView'),

	

)

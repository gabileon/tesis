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
	url(r'^perfilLinea/(?P<id_linea>.*)/edit$', 'editarLineaView'),
	url(r'^recursos/delete/(?P<id_recurso>.*)/$', 'deleteRecursoView'),
	url(r'^deleteFechas/(?P<id_evento>.*)/$', 'deleteFechasView'),
	url(r'^agregarProf/(?P<id_linea>.*)/$', 'addProfesoresView'),
	url(r'^roles/(?P<id_user>.*)/$', 'RolView'),
	url(r'^cambiarRol/(?P<id_user>.*)/(?P<rol>.*)/$', 'cambiarRolView'),
	url(r'^cambiarPassword/(?P<id_user>.*)/$', 'changePasswordView'),
	url(r'^aprobacionPrograma/(?P<id_programa>.*)/(?P<decision>.*)/$', 'aprobacionProgramaView'),
	url(r'^analisisPrograma/(?P<id_programa>.*)/(?P<decision>.*)/$', 'analisisProgramaView'),
	url(r'^reportesIndicacion/$', 'reportesIndicacionView'),
	url(r'^editFechas/(?P<id_evento>.*)/$', 'editEventosView'),
	url(r'^editRecursos/(?P<id_recurso>.*)/$', 'editRecursosView'),
	
	

)

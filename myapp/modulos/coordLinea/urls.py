from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.coordLinea.views',
	url(r'^principal_cl/$', 'principalCLView'),
	url(r'^miperfilCord/$', 'miperfilCordView'),
	url(r'^recursosCord/$', 'recursosCordView'),
	url(r'^crearFechasCord/$', 'crearFechasCoord'),
	url(r'^cambiarDatosCord/$', 'cambiarDatosCordView'),
	# url(r'^recursos/$cambiarDatosCord', 'otroPerfilView'),
	url(r'^programasAprobadosLinea/$', 'aprobadosCordViews'),
	url(r'^programasPorAnalizarLinea/$', 'preAnalisisCordView'),
	url(r'^votacionesEvaluacionLinea/$', 'votacionesEvaluacionView'),
	url(r'^votacion/(?P<id_evaluacion>.*)/$', 'votacion'),
	url(r'^votacionCordAnalisis/(?P<id_programa>.*)/$', 'votacionCordAnalisis'),
	url(r'^fastTrack/', 'fastTrackView'),

	# ul(r'^programasPorAnalizar/$', 'porAnalizarViews'),
	# url(r'^programasPorAprobar/$', 'porAprobarView'),
	# url(r'^perfilLinea/(?P<id_linea>.*)/edit$', 'editarLineaView'),
	# url(r'^recursos/delete/(?P<id_recurso>.*)/$', 'deleteRecursoView'),
	url(r'^deleteFechasCord/(?P<id_evento>.*)/$', 'deleteFechasCordView'),
	# url(r'^agregarProf/(?P<id_linea>.*)/$', 'addProfesoresView'),
	# url(r'^roles/(?P<id_user>.*)/$', 'RolView'),
	# url(r'^cambiarRol/(?P<id_user>.*)/(?P<rol>.*)/$', 'cambiarRolView'),
	url(r'^cambiarPasswordCord/(?P<id_user>.*)/$', 'changePasswordCordView'),
	# url(r'^aprobacionPrograma/(?P<id_programa>.*)/(?P<decision>.*)/$', 'aprobacionProgramaView'),
	# url(r'^analisisPrograma/(?P<id_programa>.*)/(?P<decision>.*)/$', 'analisisProgramaView'),
	url(r'^reportesIndicacionCord/$', 'reportesIndicacionCordView'),
	# url(r'^editFechas/(?P<id_evento>.*)/$', 'editEventosView'),
	# url(r'^editRecursos/(?P<id_recurso>.*)/$', 'editRecursosView'),
	url(r'^logCord/(?P<id_programa>.*)/$', 'logCordView')

	
	

)

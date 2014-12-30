from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.coordLinea.views',
	url(r'^principal_cl/$', 'principalCLView'),
	url(r'^miperfilCord/$', 'miperfilCordView'),
	url(r'^recursosCord/$', 'recursosCordView'),
	url(r'^crearFechasCord/$', 'crearFechasCoord'),
	url(r'^cambiarDatosCord/$', 'cambiarDatosCordView'),
	url(r'^programasAprobadosLinea/$', 'aprobadosCordViews'),
	url(r'^programasPorAnalizarLinea/$', 'preAnalisisCordView'),
	url(r'^votacionesEvaluacionLinea/$', 'votacionesEvaluacionView'),
	url(r'^votacion/(?P<id_evaluacion>.*)/$', 'votacion'),
	url(r'^votacionCordAnalisis/(?P<id_programa>.*)/$', 'votacionCordAnalisis'),
	url(r'^fastTrack/', 'fastTrackView'),
	url(r'^deleteFechasCord/(?P<id_evento>.*)/$', 'deleteFechasCordView'),
	url(r'^cambiarPasswordCord/(?P<id_user>.*)/$', 'changePasswordCordView'),
	url(r'^reportesIndicacionCord/$', 'reportesIndicacionCordView'),
	url(r'^logCord/(?P<id_programa>.*)/$', 'logCordView'),
	url(r'^editFechasCord/(?P<id_evento>.*)/$', 'editEventosViewCord'),
	url(r'^recursos/deleteCord/(?P<id_recurso>.*)/$', 'deleteRecursoCordView'),
	url(r'^editRecursosCord/(?P<id_recurso>.*)/$', 'editRecursosCordView'),
	

	
	

)

from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.formulacion.views',
    url(r'^definicionesGenerales/(?P<id_programa>.*)/$', 'defGenerales', name='vista_defGenerales'),
    # url(r'^programasdefiniciones/(?P<id_programa>.*)/$', 'definiciones'),
    url(r'^buscarEstado/(?P<id_programa>.*)/(?P<estado>.*)$', 'buscarEstado'),
    url(r'^definiciones/(?P<id_programa>.*)/$', 'definicionesGeneralesAdmin'),
    url(r'^definicionConstribucion/(?P<id_programa>.*)/$', 'definicionConstribucion'),
    url(r'^definicionRdA/(?P<id_programa>.*)/$', 'definicionRdA'),
    url(r'^definicionEstra/(?P<id_programa>.*)/$', 'definicionEstra'),
    url(r'^definicionclaseclase/(?P<id_programa>.*)/$', 'definicionClaseClase_view'),
    # url(r'^definicioncapacidades/(?P<id_programa>.*)/$', 'definicionCapacidades_view'),
    # url(r'^definicioncontenidos/(?P<id_programa>.*)/$', 'definicionContenidos_view'),
    url(r'^evaluacionesAsociadas/(?P<id_programa>.*)/$', 'evaluacionesAsociadasView'),
    url(r'^evaluacionesAsociadasOther/(?P<id_programa>.*)/$', 'evaluacionesAsociadasOthersView'),
    # url(r'^prueba/(?P<id_programa>.*)/$', 'definicionClaseClaseR_view'),
    url(r'^definicioncoherenciacompletitud/(?P<id_programa>.*)/$', 'definicionCompletitudCoherencia_view'),
    url(r'^aspectosAdm/(?P<id_programa>.*)/$', 'aspectosAdm_view'),
    url(r'^recursosAprend/(?P<id_programa>.*)/$', 'recursosAprend_view'),
    url(r'^intermedioAdmRec/(?P<id_programa>.*)/$', 'intermedioAdmRecView'),
    url(r'^preAnalisis/(?P<id_programa>.*)/$', 'preAnalisisView'),
    url(r'^fastTrack/(?P<id_programa>.*)/$', 'fastTrackView')


    # url(r'^resumen/(?P<id_programa>.*)/$', 'resumen2_view'),
    # url(r'^fasttrack/(?P<id_programa>.*)/$', 'fasttrack_view'),
    # url(r'^aprobacion/(?P<id_programa>.*)/$', 'aprobacionPrograma_view'),
    # url(r'^analisis/(?P<id_programa>.*)/$', 'analisisPrograma_view')
)
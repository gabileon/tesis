from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.formulacion.views',
    url(r'^definicionesGenerales/(?P<id_programa>.*)/$', 'defGenerales', name='vista_defGenerales'),
    url(r'^buscarEstado/(?P<id_programa>.*)/(?P<estado>.*)$', 'buscarEstado'),
    url(r'^definiciones/(?P<id_programa>.*)/$', 'definicionesGeneralesAdmin'),
    url(r'^definicionConstribucion/(?P<id_programa>.*)/$', 'definicionConstribucion'),
    url(r'^definicionRdA/(?P<id_programa>.*)/$', 'definicionRdA'),
    url(r'^definicionEstra/(?P<id_programa>.*)/$', 'definicionEstra'),
    url(r'^definicionclaseclase/(?P<id_programa>.*)/$', 'definicionClaseClase_view'),
    url(r'^definicioncoherenciacompletitud/(?P<id_programa>.*)/$', 'definicionCompletitudCoherencia_view'),
    url(r'^aspectosAdm/(?P<id_programa>.*)/$', 'aspectosAdm_view'),
    url(r'^recursosAprend/(?P<id_programa>.*)/$', 'recursosAprend_view'),
    url(r'^intermedioAdmRec/(?P<id_programa>.*)/$', 'intermedioAdmRecView'),
    url(r'^fastTrackDecision/(?P<id_programa>.*)/(?P<decision>.*)/$', 'fastTrackDecisionView'),
    ###### analisis ####
    url(r'^votacionAnalisisProfe/(?P<id_programa>.*)/$', 'votacionAnalisisProfeView'),
    url(r'^votacionAnalisisOtroProfe/$', 'votacionAnalisisOtroProfeView'),
    url(r'^votacionOtroProfe/(?P<id_programa>.*)/$', 'votacionOtroProfeView'),
    ######## evaluaciones #####
    url(r'^evaluacionesAsociadas/(?P<id_programa>.*)/$', 'evaluacionesAsociadasView'),
    url(r'^votacionesEvaluacionOtroProfeLinea/$', 'evaluacionesAsociadasOthersView' ),
    url(r'^votacionesEvaluacionOtroProfe/(?P<id_programa>.*)/$', 'votacionEvaluacionOtroProfeView' ),
    url(r'^analisisProgramaJC/(?P<id_programa>.*)/$', 'analisisProgramaJCView' ),
    url(r'^fastTrackOwn/(?P<id_programa>.*)/$', 'fastTrackOwnView' ),
    url(r'^aprobacionProgramaJC/(?P<id_programa>.*)/$', 'aprobacionProgramaJCView' ),





    
    

)
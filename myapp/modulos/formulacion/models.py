from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import get_storage_class
from django_xworkflows import models as xwf_models
import xworkflows
from myapp import settings
from time import time


class MyWorkflow(xwf_models.Workflow):
    log_model = '' # Disable logging to database

##################### DECLARACION DE ESTADOS ##########################
    states = (
        ('inicio', (u"Inicio")),
        ('formulacionPrograma', (u"Formulacion Programa por Linea")),
        ('definicionDatosAsignatura', (u"Definicion Datos Asignatura")),
        ('definicionGeneral', (u"Definiciones Generales")),
        ('definicionConstribucion', (u"Definicion de Constribucion al Perfil de Egreso ")),
        ('definicionRdA', (u"Definicion Resultados de Aprendizaje")),
        ('definicionEstrategias', (u"Estrategias de Ensenanza y de Aprendizaje")),
        ('definicionClaseClase', (u"Definicion de Clase a Clase")),
        ('analisisEvaluacionesAsociadas', (u"Analisis de evaluaciones asociadas")),
        ('verificacionCoherenciaCompletitud', (u"Verificacion Coherencia y Completitud")),
        ('programacionActividades', (u"Programacion de Actividades")),
        ('definicionAspecAdmin', (u"Definicion de Aspectos Administrativos")),
        ('definicionRecursos', (u"Definicion de Recursos de Aprendizaje")),
        ('aprobacionLinea', (u"Aprobacion Linea")),
        ('fastTrack', (u"Fast Track")),
        ('analisisProgramaJC', (u"Analisis Programa por JC")),
        ('indicacionModificacion', (u"Existen Indicaciones de Modificacion")),
        ('aprobacionProgramaJC', (u"Aprobacion Programa por JC")),
        ('fin', (u"Fin")),
    )

    ##################### DECLARACION DE TRANSICIONES ##########################
    transitions = (
        ('to_formulacion', 'inicio', 'formulacionPrograma'),
        ('to_datosAsig', 'formulacionPrograma', 'definicionDatosAsignatura' ),
        ('to_defGeneralCons', 'definicionConstribucion', 'definicionGeneral'),
        ('to_defGeneralRdA', 'definicionRdA', 'definicionGeneral'),
        ('to_defGeneralEstra', 'definicionEstrategias', 'definicionGeneral'),
        ('to_defGeneral', 'definicionDatosAsignatura', 'definicionGeneral'),
        ('to_defCons', 'definicionGeneral', 'definicionConstribucion'),
        ('to_defRdA', 'definicionGeneral', 'definicionRdA'),
        ('to_defEstrategias', 'definicionGeneral', 'definicionEstrategias'),
        ('to_defClase', ('definicionEstrategias', 'definicionConstribucion', 'definicionRdA'), 'definicionClaseClase'),
        ('to_analisisEval', 'definicionClaseClase', 'analisisEvaluacionesAsociadas'),
        ('noEvaluacion_toForm', 'analisisEvaluacionesAsociadas', 'formulacionPrograma'),
        ('siEvaluacion_toVerif', 'analisisEvaluacionesAsociadas', 'verificacionCoherenciaCompletitud'),
        ('to_programacion', 'analisisEvaluacionesAsociadas', 'programacionActividades'),
        ('to_defAspectos', 'programacionActividades', 'definicionAspecAdmin'),
        ('to_defRecursos', 'programacionActividades', 'definicionRecursos'),
        ('to_aprobPrograma', ('definicionRecursos','definicionAspecAdmin'), 'aprobacionLinea'),
        ('noAprob_toForm', 'aprobacionLinea', 'formulacionPrograma'),
        ('siAprob_toFT', 'aprobacionLinea', 'fastTrack'),
        ('siFT_toAprobJC', 'fastTrack', 'aprobacionProgramaJC'),
        ('noFT_toAnalisisJC', 'fastTrack', 'analisisProgramaJC'),
        ('to_indicModif', 'analisisProgramaJC', 'indicacionModificacion'),
        ('noIndic_toAprobJC', 'indicacionModificacion', 'aprobacionProgramaJC'),
        ('siIndic_toForm', 'indicacionModificacion', 'formulacionPrograma'),
        ('siAprob_toFin', 'aprobacionProgramaJC', 'fin'),
        ('noAprobJC_toForm', 'aprobacionProgramaJC', 'formulacionPrograma'),
        #  ('to_def', 'definicionGeneral', ('definicionObjetivos', 'definicionCapacidades', 'definicionContenidos')),    
     ######### ESTADO INICIAL #########       
    )
    initial_state = 'inicio'

    ## Se crea modelo Programa 

class Programa(xwf_models.WorkflowEnabled, models.Model):
# SE DEFINE SU ESTADO QUE ESTA DADO POR EL WORKFLOW DEFINIDO ###
    state = xwf_models.StateField(MyWorkflow)
    asignatura =  models.CharField(max_length=100)
    semestre =  models.CharField(max_length=10)
    ano =  models.CharField(max_length=10)
    fechaUltimaModificacion = models.DateTimeField()
    url = models.URLField(blank=False, null=True)
    profesorEncargado = models.OneToOneField(User, null=True)

    
class Capacidad(models.Model):
    programa = models.OneToOneField(Programa)
    estadoCapac  = models.CharField(max_length=10, default="Sin iniciar")
    capacidadesPrograma = models.TextField()
    ultimaModificacionCapac = models.DateTimeField(auto_now=True)

class Contenido(models.Model): 
    programa = models.OneToOneField(Programa)
    contenidosPrograma = models.TextField()
    estadoCont = models.CharField(max_length=10, default="Sin iniciar")
    ultimaModificacionCont = models.DateTimeField(auto_now=True)

class Objetivo (models.Model):
    programa = models.OneToOneField(Programa)
    objetivosPrograma = models.TextField()
    estadoObj = models.CharField(max_length=10, default="Sin iniciar")
    ultimaModificacionObj = models.DateTimeField(auto_now=True)

class ClaseClase (models.Model):
    programa = models.OneToOneField(Programa)
    claseclase = models.TextField()
    estadoClase = models.CharField(max_length=10, default="Sin iniciar")
    ultimaModificacionClase  = models.DateTimeField(auto_now=True)

class Completitud(models.Model):
    programa = models.OneToOneField(Programa)
    estadoComp = models.CharField(max_length=10, default="Sin iniciar")
    ultimaModificacionComp = models.DateTimeField(auto_now=True)
    completitudPrograma = models.TextField()

class Linea(models.Model):
    coordinador = models.OneToOneField(User, null=True)
    nombreLinea = models.CharField(max_length=20)

class Asignatura(models.Model):
    nombreAsig = models.CharField(max_length=20)
    plan = models.CharField(max_length=5)
    profesorAsignado = models.OneToOneField(User, null=True)
    linea = models.ForeignKey(Linea)

class Recurso(models.Model):
    def url(self, filename):
        url = "MultimediaData/Recursos/%s"%(filename)
        return url
        
    titulo_recurso =  models.CharField(max_length=100)
    descripcion_recurso = models.TextField()
    estado = models.CharField(max_length=20, default="Generales")
    fechaUltimaModificacion = models.DateTimeField()
    recurso = models.FileField(upload_to=url)


 

    
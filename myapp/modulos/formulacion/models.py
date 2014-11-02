from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import get_storage_class
from django_xworkflows import models as xwf_models
from myapp.modulos.coordLinea.models import Coordinador
from myapp.modulos.profLinea.models import Profesor
import xworkflows



class MyWorkflow(xwf_models.Workflow):
    log_model = '' # Disable logging to database

##################### DECLARACION DE ESTADOS ##########################
    states = (
        ('inicio', (u"Inicio")),
        ('formulacionPrograma', (u"Formulacion Programa por Linea")),
        ('definicionGeneral', (u"Definiciones Generales")),
        ('definicionCapacidades', (u"Definiciones Capacidades")),
        ('definicionContenidos', (u"Definiciones Contenidos")),
        ('definicionObjetivos', (u"Definiciones Objetivos")),
        ('definicionClaseClase', (u"Definiciones de Clase a Clase")),
        ('analisisEvaluacionesAsociadas', (u"Analisis de evaluaciones asociadas")),
        ('verificacionCoherenciaCompletitud', (u"Verificacion Coherencia y Completitud")),
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
        ('to_defGeneralObj', 'definicionObjetivos', 'definicionGeneral'),
        ('to_defGeneralCap', 'definicionCapacidades', 'definicionGeneral'),
        ('to_defGeneralCont', 'definicionContenidos', 'definicionGeneral'),
        ('to_defGeneral', 'formulacionPrograma', 'definicionGeneral'),
        ('to_defObj', 'definicionGeneral', 'definicionObjetivos'),
        ('to_defCap', 'definicionGeneral', 'definicionCapacidades'),
        ('to_defCont', 'definicionGeneral', 'definicionContenidos'),
        ('to_defClase', ('definicionObjetivos', 'definicionContenidos', 'definicionCapacidades'), 'definicionClaseClase'),
        ('to_analisisEval', 'definicionClaseClase', 'analisisEvaluacionesAsociadas'),
        ('noEvaluacion_toForm', 'analisisEvaluacionesAsociadas', 'formulacionPrograma'),
        ('siEvaluacion_toVerif', 'analisisEvaluacionesAsociadas', 'verificacionCoherenciaCompletitud'),
        ('to_aprobPrograma', 'verificacionCoherenciaCompletitud', 'aprobacionLinea'),
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
    I = 'I'
    II = 'II'
    semestre_opciones = (
        (I, 'I Semestre'),
        (II, 'II Semestre'))
    asignatura =  models.CharField(max_length=100)
    semestre =  models.CharField(max_length=2, choices=semestre_opciones)
    semestre =  models.CharField(max_length=10)
    ano =  models.CharField(max_length=10)
    fechaUltimaModificacion = models.DateTimeField()
    # fechaCreacion = models.DateTimeField(auto_now_add=True)
    
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
    coordinador = models.OneToOneField(Coordinador, null=True)
    nombreLinea = models.CharField(max_length=20)

class Asignatura(models.Model):
    nombreAsig = models.CharField(max_length=20)
    plan = models.CharField(max_length=5)
    carrera = models.CharField(max_length=20)
    profesorAsignado = models.OneToOneField(Profesor)
    
    

    
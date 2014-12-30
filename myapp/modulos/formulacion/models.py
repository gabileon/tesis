from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import get_storage_class
from django_xworkflows import models as xwf_models
import xworkflows
from myapp import settings
from time import time
from djangotoolbox.fields import ListField

class ListaField(ListField):
    def formfield(self, **kwargs):
        return models.Field.formfield(self, StringListField, **kwargs)


class Linea(models.Model):
    coordinador = models.OneToOneField(User, null=True)
    nombreLinea = models.CharField(max_length=20)
    carpetaReportes = models.CharField(max_length=40)
    carpeta = models.CharField(max_length=40)

class Asignatura(models.Model):
    nombreAsig = models.CharField(max_length=20)
    plan = models.CharField(max_length=5)
    linea = models.ForeignKey(Linea, null=True)


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
        ('definicionAspecAdmin', (u"Definicion de Aspectos Administrativos")),
        ('definicionRecursos', (u"Definicion de Recursos de Aprendizaje")),
        ('definicionAspectosFinales' , (u"Definicion de Aspectos Finales")),
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
        ('to_defGeneralClase', 'definicionClaseClase', 'definicionGeneral'),
        ('to_defGeneral', 'definicionDatosAsignatura', 'definicionGeneral'),
        ('to_defCons', 'definicionGeneral', 'definicionConstribucion'),
        ('to_defRdA', 'definicionGeneral', 'definicionRdA'),
        ('to_defEstrategias', 'definicionGeneral', 'definicionEstrategias'),
        ('to_defClase', ('definicionEstrategias', 'definicionConstribucion', 'definicionRdA'), 'definicionClaseClase'),
        ('to_analisisEval', 'definicionClaseClase', 'analisisEvaluacionesAsociadas'),
        ('noEvaluacion_toForm', 'analisisEvaluacionesAsociadas', 'formulacionPrograma'),
        ('siEvaluacion_toVerif', 'analisisEvaluacionesAsociadas', 'verificacionCoherenciaCompletitud'),
        ('verificacion_toAspectosFinal', 'verificacionCoherenciaCompletitud', 'definicionAspectosFinales'),
        ('to_AdmAspectos', 'definicionAspecAdmin', 'definicionAspectosFinales'),
        ('to_RecAspectos', 'definicionRecursos', 'definicionAspectosFinales'),
        ('to_defAspectos', 'definicionAspectosFinales', 'definicionAspecAdmin'),
        ('to_defRecursos', 'definicionAspectosFinales', 'definicionRecursos'),
        ('to_aprobPrograma', ('definicionRecursos','definicionAspecAdmin'), 'aprobacionLinea'),
        ('noAprob_toForm', 'aprobacionLinea', 'formulacionPrograma'),
        ('siAprob_toFT', 'aprobacionLinea', 'fastTrack'),
        ('siFT_toAprobJC', 'fastTrack', 'aprobacionProgramaJC'),
        ('noFT_toAnalisisJC', 'fastTrack', 'analisisProgramaJC'),
        ('noIndic_toAprobJC', 'analisisProgramaJC', 'aprobacionProgramaJC'),
        ('siIndic_toForm', 'analisisProgramaJC', 'formulacionPrograma'),
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
    asignatura =  models.OneToOneField(Asignatura, null=True)
    semestre =  models.CharField(max_length=10)
    ano =  models.CharField(max_length=10)
    fechaUltimaModificacion = models.DateTimeField()
    url = models.URLField(blank=False, null=True)
    profesorEncargado = models.OneToOneField(User, null=True)
    id_file =  models.CharField(max_length=100)

class Log(models.Model):
    programa = models.OneToOneField(Programa)
    fecha = models.DateTimeField()
    state = models.CharField(max_length=20)
    
    
class Constribucion(models.Model):
    programa = models.OneToOneField(Programa)
    estado  = models.CharField(max_length=10, default="Sin iniciar")

class RDA(models.Model): 
    programa = models.OneToOneField(Programa)
    estado = models.CharField(max_length=10, default="Sin iniciar")

class Estrategias (models.Model):
    programa = models.OneToOneField(Programa)
    estado = models.CharField(max_length=10, default="Sin iniciar")

class ClaseClase (models.Model):
    programa = models.OneToOneField(Programa)
    estado = models.CharField(max_length=10, default="Sin iniciar")

class Completitud(models.Model):
    programa = models.OneToOneField(Programa)
    estado= models.CharField(max_length=10, default="Sin iniciar")

class Administrativo(models.Model):
    programa = models.OneToOneField(Programa)
    estado= models.CharField(max_length=10, default="Sin iniciar")

class RecursosApren(models.Model):
    programa = models.OneToOneField(Programa)
    estado= models.CharField(max_length=10, default="Sin iniciar")

class Evaluacion (models.Model):
    programa = models.OneToOneField(Programa)
    votoEvalCord = models.BooleanField(default=False)
    votoProfe = models.BooleanField(default=False)

class Evaluaciones(models.Model):
    voto = models.CharField(max_length=2)
    votante = models.OneToOneField(User)
    observacion = models.TextField()
    evaluacion = models.OneToOneField(Evaluacion)
    cord = models.BooleanField(default=False)

class AnalisisM(models.Model):
    programa = models.OneToOneField(Programa)
    votoEvalCord = models.BooleanField(default=False)
    votoProfe = models.BooleanField(default=False)

class Analisis(models.Model):
    voto = models.CharField(max_length=2)
    votante = models.OneToOneField(User)
    observacion = models.TextField()
    analisis = models.OneToOneField(AnalisisM)
    cord = models.BooleanField(default=False)


class Recurso(models.Model):
    def url(self, filename):
        url = "MultimediaData/Recursos/%s"%(filename)
        return url
        
    titulo_recurso =  models.CharField(max_length=100)
    descripcion_recurso = models.TextField()
    estado = models.CharField(max_length=20, default="Generales")
    fechaUltimaModificacion = models.DateTimeField()
    recurso = models.FileField(upload_to=url)
    creador = models.OneToOneField(User, null=True)

class Profesor (models.Model):
    user =  models.OneToOneField(User, null=True)
    linea = models.ForeignKey(Linea, null=True)


 

    
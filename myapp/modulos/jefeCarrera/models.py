from django.db import models
from django import forms 
from djangotoolbox.fields import ListField
from myapp.modulos.formulacion.models import Programa



class Evento(models.Model):
	summary = models.CharField(max_length=100)
	location = models.CharField(max_length=100)
	start = models.DateTimeField()
	end = models.DateTimeField()
	descripcion = models.TextField()
	tipoEvento = models.CharField(max_length=100)
	id_calendar = models.CharField(max_length=100)

class ReporteIndic(models.Model):
	programa = models.OneToOneField(Programa)
	fechaModificacion = models.DateField()
	url = models.URLField(blank=False, null=True)
	carpeta = models.CharField(max_length=100, null=True)

from django.db import models
from django import forms 
from djangotoolbox.fields import ListField
from myapp.modulos.formulacion.models import Programa
from django.contrib.auth.models import User



class Evento(models.Model):
	summary = models.CharField(max_length=100)
	location = models.CharField(max_length=100)
	fecha = models.CharField(max_length=100)
	start = models.CharField(max_length=100)
	end = models.CharField(max_length=100)
	descripcion = models.TextField()
	tipoEvento = models.CharField(max_length=100)
	id_calendar = models.CharField(max_length=100)
	anfitrion = models.OneToOneField(User, null=True)
	invitados = ListField()


class ReporteIndic(models.Model):
	programa = models.OneToOneField(Programa)
	fechaModificacion = models.DateField()
	url = models.URLField(blank=False, null=True)
	carpeta = models.CharField(max_length=100, null=True)

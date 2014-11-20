from django.db import models
from django import forms 
from djangotoolbox.fields import ListField

class ListaField(ListField):
    def formfield(self, **kwargs):
        return models.Field.formfield(self, StringListField, **kwargs)


class Evento(models.Model):
	summary = models.CharField(max_length=100)
	location = models.CharField(max_length=100)
	start = models.DateTimeField()
	end = models.DateTimeField()
	descripcion = models.TextField()
	attendees =  ListaField()




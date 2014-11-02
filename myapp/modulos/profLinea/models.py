from django.db import models
from myapp.modulos.presentacion.models import UserProfile
# from myapp.modulos.coordLinea.models import Coordinador
# from myapp.modulos.formulacion.models import Linea
from django.contrib.auth.models import User


# Create your models here.

class Profesor(models.Model):
    profile= models.OneToOneField(UserProfile, related_name='Profesor_profile')
    fechaAsigna = models.DateTimeField()
    linea = models.ManyToManyField('formulacion.Linea')
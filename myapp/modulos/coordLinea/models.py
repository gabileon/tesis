from django.db import models
from myapp.modulos.presentacion.models import UserProfile
from django.contrib.auth.models import User

# Create your models here.
class Coordinador(models.Model):
    profile= models.OneToOneField(UserProfile, related_name='Coordinador_profile')
    fechaAsigna = models.DateTimeField()

    def __unicode__(self):
        pass
    
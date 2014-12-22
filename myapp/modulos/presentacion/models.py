from django.db import models
from django.contrib.auth.models import User
from oauth2client.django_orm import CredentialsField
from myapp.modulos.formulacion.models import Linea
from djangotoolbox.fields import ListField

class UserProfile(models.Model):
	def url(self, filename):
		ruta = "MultimediaData/Users/%s/%s"%(self.user.username, filename)
		return ruta
	
	user = models.OneToOneField(User)
	rol_JC = models.CharField(max_length=250, blank=True)
	rol_PL = models.CharField(max_length=250, blank=True)
	rol_CL = models.CharField(max_length=250, blank=True)
	rol_actual = models.CharField(max_length=250, blank=True)
	foto = models.ImageField("Foto de Perfil", upload_to=url, default= 'media/img/user-default.png')
	cordLinea = models.ForeignKey(Linea, null=True, related_name='coordinador_linea')
	carpetaProgramas = models.CharField(max_length=250, default= "NO CREADA")
	carpetaReportes = models.CharField(max_length=250, null=True, default= "NO CREADA" )
	fechaPrimerAcceso = models.DateTimeField(null=True)
	def create_user_profile(sender, instance, created, **kwargs):  
		if created:  
			profile, created = UserProfile.objects.get_or_create(user=instance)


class CredentialsModel(models.Model):
	id_user = models.ForeignKey(User, unique=True)
	credential = CredentialsField()
	





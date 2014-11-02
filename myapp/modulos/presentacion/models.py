from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	def url(self, filename):
		ruta = "MultimediaData/Users/%s/%s"%(self.user.username, filename)
		return ruta
	
	username = models.OneToOneField(User, related_name='user_profile')
	rol = models.CharField(max_length=250, blank=True)
	foto = models.ImageField("Profile Pic", upload_to="images/", default= 'media/img/user-default.png')
	# telefono = models.PositiveIntegerField()
	linea = models.CharField(max_length=250, blank=True)

	def create_user_profile(sender, instance, created, **kwargs):  
		if created:  
			profile, created = UserProfile.objects.get_or_create(user=instance)
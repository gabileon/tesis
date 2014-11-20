from django.contrib import admin
from myapp.modulos.presentacion.models import UserProfile,CredentialsModel

admin.site.register(UserProfile)

class CredentialsAdmin(admin.ModelAdmin):
	pass

admin.site.register(CredentialsModel, CredentialsAdmin)
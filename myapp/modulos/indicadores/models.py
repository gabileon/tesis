from django.db import models
from myapp.modulos.formulacion.models import Programa
# Create your models here.

class MonthlyWeatherByCity(models.Model):
    month = models.IntegerField()
    boston_temp = models.DecimalField(max_digits=5, decimal_places=1)
    houston_temp = models.DecimalField(max_digits=5, decimal_places=1)

   
class DailyWeather(models.Model):
    month = models.IntegerField()
    day = models.IntegerField()
    temperature = models.DecimalField(max_digits=5, decimal_places=1)
    rainfall = models.DecimalField(max_digits=5, decimal_places=1)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)

class ProgramasPorEstado (models.Model):
	estado =  models.CharField(max_length=50)
	cantidad = models.IntegerField()

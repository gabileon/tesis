from django.shortcuts import render
from chartit import DataPool, Chart
from myapp.modulos.indicadores.models import MonthlyWeatherByCity, ProgramasPorEstado
from myapp.modulos.formulacion.models import Programa
from django.shortcuts import render_to_response, get_object_or_404
from datetime import datetime

def weather_chart_view(request):
  username = request.user.username
 

  ds = DataPool(
  series=
  [{'options': {
  'source': ProgramasPorEstado.objects.all()},
  'terms': [
          'estado',
           'cantidad']}
           ])
  cht = Chart(
       datasource = ds, 
       series_options = 
          [{'options':{
            'type': 'column',
            'stacking':True},
          'terms':{
            'estado': [
              'cantidad'                ]
            }}],
  chart_options = 
       {'title': {
             'text': 'Programas por Estados'},
       'xAxis': {
              'title': {
                'text': 'Estados'}}})

     #Step 3: Send the chart object to the template.
  return render(request, 'indicadores/prueba.html', {'weatherchart': cht, 'username':username})


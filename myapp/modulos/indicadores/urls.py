from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.indicadores.views',
    url(r'^prueba/$', 'weather_chart_view'),
    )
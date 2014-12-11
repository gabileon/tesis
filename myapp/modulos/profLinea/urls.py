from django.conf.urls import patterns, url

urlpatterns = patterns('myapp.modulos.profLinea.views',
    url(r'^principalPL/$', 'principalPLView', name='principalPL_view'),
)
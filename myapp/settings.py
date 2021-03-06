# Django settings for myapp project.

# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file

### Added for GAE
#### export PATH="/home/gabi/google_appengine:$PATH"

from djangoappengine.settings_base import *
import os



ADMINS = (
    ('Gabriela Leon', 'gabi.leon.f@gmail.com'),
)
MANAGERS = ADMINS


# Activate django-dbindexer for the default database
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': DATABASES['default']}

AUTOLOAD_SITECONF = 'indexes'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['programas-diinf.appspot.com']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Santiago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), 'media/'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7e&clpg0_t!icq%+od264e=ap_+3i%m+e*abl6=cm&*x1xfhe*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'myapp.urls'

                      #####Perfil de Usuarios #########
AUTH_PROFILE_MODULE = 'presentacion.UserProfile'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes,o even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'myapp.modulos.presentacion',
    'myapp.modulos.formulacion',
    'myapp.modulos.jefeCarrera',
    'myapp.modulos.coordLinea',
    'myapp.modulos.profLinea',
    'myapp.modulos.indicadores',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    'xworkflows',
    'django_xworkflows',
    'django_forms_bootstrap',
    'gaeblob_storage',
    'simplejson',
    'highcharts',
    'chartit',
    'datetimewidget',
    'djangoappengine',
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LANGUAGES = ('es', 'Spanish')
DATE_INPUT_FORMATS = ('%d-%m-%Y')

DATETIME_INPUT_FORMATS  = ('%d-%m-%Y %H:%M:%S')

EMAIL_BACKEND = 'djangoappengine.mail.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'programasdiinf'
# EMAIL_HOST_PASSWORD =  'programasdiinf2014'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#REDIRECT_URI = 'http://localhost:8000/oauth2callback/'
REDIRECT_URI = 'http://programas-diinf.appspot.com/oauth2callback/'
DEFAULT_FILE_STORAGE = 'gaeblob_storage.backends.BlobPropertyStorage'

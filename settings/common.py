import sys, os
from socket import herror
from deployment.path_settings import PROJECT_ROOT

from private.database_settings import DATABASE_DICT


ADMINS = (
    ('Justin Holmes', 'justin@justinholmes.com'),
    ('Amanda Stauble', 'ac.stauble@gmail.com'),
    ('Dominick Piaquadio', 'dpiaquadio@gmail.com'),
    ('Kieran Prasch', 'kieranprasch@gmail.com'),
    ('Max Orloff', 'mr.offalox@gmail.com'),
    
    ('Rachel Lagodka', 'rachel.lagodka@gmail.com'),
    
    ('Andrew Mischo','8454188198@vtext.com'),
    ('James Farrington', 'sonsof70@yahoo.com'),
)

MANAGERS = ADMINS

if 'test' in sys.argv or 'test_coverage' in sys.argv:
    DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'test_db', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
        }
    }

else:
    DATABASES = {
                 
        #Production DB on margaret
        'default': DATABASE_DICT
    
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '%s/static' % PROJECT_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media_admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n+^kdwedcy=9_!&zkb_b#0^)x)h513a%9&+@-!4@v1oq!+xujz'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.doc.XViewMiddleware'
]


ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    '%s/templates/' % PROJECT_ROOT
)

CORE_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'django_coverage',
)

PACKAGED_APPS = (
     'south',
     'taggit',
     #'debug_toolbar',
     #'haystack',
)


LOCAL_APPS = (    
    'utility',
    'people',
    'products',
    'hwtrack',   
    'accounting',
    'checklist',
    'cms',
    'comm',
    'contact',
    'meta',
    'main',
    'mooncalendar',
    'pigs',
    'power',
    'pos',
    'presence',
    'service',
    'sandbox',
    'social',
    'do',
    'commerce',
    'mellon',
)

INSTALLED_APPS = PACKAGED_APPS + CORE_APPS + LOCAL_APPS


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://margaret:8983/solr/',
        'TIMEOUT': 60 * 5,
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
    },
}

EMAIL_HOST = 'smtp-server.hvc.rr.com'

AUTH_PROFILE_MODULE = 'people.UserProfile'
LOGIN_URL = '/presence/login/'

TINYMCE_JS_URL = '/media/js/tiny_mce/tiny_mce_src.js'

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    'theme': "advanced",
}

TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = True

COVERAGE_REPORT_HTML_OUTPUT_DIR = '/home/slashroot/'

#LOCAL SETTINGS
PUBLIC_FILE_UPLOAD_DIRECTORY = '%s/public/' % MEDIA_ROOT

LOGIN_REDIRECT_URL = "/iam/"

#VARNISH_MANAGEMENT_ADDRS = ['50.57.232.77:2000']

#Override the Test Runner to test only local apps.

TEST_RUNNER = 'utility.tests.WHATTestRunner'
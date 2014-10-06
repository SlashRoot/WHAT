from common import *
from private.database_settings import PRODUCTION_DATABASE_DICT

DEBUG = True
TEMPLATE_DEBUG = DEBUG

PORT = 5150

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'what',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'Video$)$)',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5555',                      # Set to empty string for default. Not used with sqlite3.
    }
}


#Uncomment to use production data (you'll need access to private repo, of course.)
DATABASES = {
    #Production DB on margaret
    'default': PRODUCTION_DATABASE_DICT
}

DATABASES['default']['PORT'] = 5555

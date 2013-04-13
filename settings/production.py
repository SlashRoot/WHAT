from settings.common import *
from private.database_settings import PRODUCTION_DATABASE_DICT as DATABASE_DICT

DEBUG = False
#PUBLIC_FILE_UPLOAD_DIRECTORY = '/home/slashroot/what-production/static/public/'

MIDDLEWARE_CLASSES.append('what_apps.meta.errors.ServerErrorMiddleware')
SERVER_EMAIL = 'production-errors@slashrootcafe.com'
PORT = 8080

DATABASES = {
             
    #Production DB on margaret
    'default': DATABASE_DICT

}

from settings.common import *

DEBUG = False
#PUBLIC_FILE_UPLOAD_DIRECTORY = '/home/slashroot/what-production/static/public/'

MIDDLEWARE_CLASSES.append('what_apps.meta.errors.ServerErrorMiddleware')
SERVER_EMAIL = 'production-errors@slashrootcafe.com'
PORT = 8080

from settings.common import *

DEBUG = False
#PUBLIC_FILE_UPLOAD_DIRECTORY = '/home/slashroot/what-production/static/public/'

MIDDLEWARE_CLASSES.append('meta.errors.ServerErrorMiddleware')
SERVER_EMAIL = 'production-errors@slashrootcafe.com'
PRODUCTION_SERVER_PORT = 8080
STAGING_SERVER_PORT = 3080
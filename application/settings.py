import os

#from secret_keys import CSRF_SECRET_KEY, SESSION_KEY


DEBUG_MODE = True

# Auto-set debug mode based on App Engine dev environ
#if 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
#    DEBUG_MODE = True

DEBUG = DEBUG_MODE


CSRF_ENABLED = True
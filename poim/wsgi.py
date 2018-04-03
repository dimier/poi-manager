import os
import sys

sys.dont_write_bytecode = True

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "poim.settings")

application = get_wsgi_application()


# Preload app

from django.urls import resolve
try:
    resolve('/')
except Exception:
    pass

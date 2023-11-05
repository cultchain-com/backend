"""
WSGI config for cultchian_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application
from .settings import BASE_DIR

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cultchian_backend.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root='/usr/src/app/static')
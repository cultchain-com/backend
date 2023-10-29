from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the Celery app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cultchian_backend.settings')
app = Celery('cultchian_backend')

# Use the Django settings for the Celery app
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

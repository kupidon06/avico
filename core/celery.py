import os
from celery import Celery

# Charger les paramètres Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Charger les paramètres Celery à partir de Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discovery des tâches dans les applications Django
app.autodiscover_tasks()

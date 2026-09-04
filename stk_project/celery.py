import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stk_project.settings.dev')

app = Celery('stk_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
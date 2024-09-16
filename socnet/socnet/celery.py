import os

from celery import Celery


# подключаем celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "socnet.settings")
app = Celery("socnet")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

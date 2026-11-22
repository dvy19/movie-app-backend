
import os
from celery import Celery

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Celery application
app = Celery("config")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Automatically discover tasks.py in installed Django apps
app.autodiscover_tasks()


# celery -A config worker --loglevel=info --pool=solo
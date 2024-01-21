from django.apps import AppConfig
from . import yolo

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    model = yolo.yolo()

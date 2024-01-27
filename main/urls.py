from django.urls import path, include
from . import views

app_name = "main"
urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('upload/', views.upload, name='upload'),
]

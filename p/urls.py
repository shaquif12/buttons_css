from django.urls import path
from chat import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.chat_view, name='chat'),
]
